"""Deterministic verification against the SEBI register snapshot (F08, ADR-010).

Key rules:
- Not found != fraud. A well-formed number missing from the snapshot is NOT_VERIFIED, never
  CONTRADICTED (the snapshot can be stale), so ADR-006 keeps it at NEEDS VERIFICATION.
- CONTRADICTED needs positive evidence: the number belongs to a clearly different company,
  or the registration has expired.
- A registered entity proves the entity exists, not that the person contacting the user
  represents it. A VERIFIED record never cancels a critical signal (enforced in assess()).
- No verification depends on the LLM. Records are written only by the backend (ADR-007).
"""

from datetime import date

from app.engine.patterns import REG_NO_PREFIXES, SEBI_OFFER_TYPES, find_reg_numbers
from app.engine.registry import DIFFERENT_THRESHOLD, MATCH_THRESHOLD, Registry, RegistryEntry, name_tokens
from app.models import Facts, SourceTier, VerificationRecord, VerificationStatus

NON_SEBI_OFFER_TYPES = {"mlm", "job", "loan"}
IMPERSONATION_NOTE = (
    "This confirms the entity is registered; it does not confirm the person contacting you represents it. "
    "Contact them only via the details listed on SEBI's site."
)


def _source(registry: Registry, entry: RegistryEntry | None = None) -> str:
    snapshot = registry.snapshot_date.isoformat() if registry.snapshot_date else "unknown date"
    what = f"SEBI register of {entry.category}s" if entry else "SEBI registers of intermediaries"
    return f"{what} (snapshot {snapshot})"


def _entry_evidence(entry: RegistryEntry) -> str:
    validity = f"valid till {entry.valid_till.isoformat()}" if entry.valid_till else "perpetual registration"
    trade = f" (trade name: {entry.trade_name})" if entry.trade_name and entry.trade_name != entry.name else ""
    return f"{entry.reg_no} is registered to {entry.name}{trade} as a {entry.category}, {validity}. Source: {entry.source_url}"


def _entry_params(registry: Registry, entry: RegistryEntry) -> dict[str, str]:
    return {
        "reg_no": entry.reg_no,
        "registered_name": entry.name,
        "category": entry.category,
        "valid_till": entry.valid_till.isoformat() if entry.valid_till else "",
        "snapshot_date": registry.snapshot_date.isoformat() if registry.snapshot_date else "",
    }


def _record(code: str, status: VerificationStatus, tier: SourceTier, claim: str, source: str, evidence: str,
            explanation: str, params: dict[str, str], material: bool = True) -> VerificationRecord:
    return VerificationRecord(code=code, params=params, claim=claim, source=source, source_tier=tier, status=status,
                              evidence=evidence, explanation=explanation, material=material)


def _check_reg_no(reg_no: str, well_formed: bool, names: list[str], person_names: list[str], registry: Registry,
                  today: date) -> VerificationRecord:
    claim = f"SEBI registration number {reg_no}"
    if not well_formed:
        return _record(
            "REG_MALFORMED", VerificationStatus.NOT_VERIFIED, SourceTier.USER_PROVIDED, claim, "Number format check",
            f"{reg_no} does not match SEBI's format (for example INA, INH or INZ followed by 9 digits).",
            "This doesn't look like a valid SEBI registration number. Ask them to confirm it, then check it on "
            "sebi.gov.in.",
            {"reg_no": reg_no},
        )
    if not registry.available or reg_no[:3] not in registry.prefixes:
        category = REG_NO_PREFIXES.get(reg_no[:3], "this category")
        return _record(
            "REG_CATEGORY_NOT_COVERED", VerificationStatus.NOT_VERIFIED, SourceTier.OFFICIAL_REGULATOR, claim,
            _source(registry), f"Our snapshot does not include SEBI's list of {category}s.",
            "We couldn't check this number automatically. That doesn't mean it's fake: check it on sebi.gov.in.",
            {"reg_no": reg_no, "category": category},
        )
    entry = registry.lookup(reg_no)
    if entry is None:
        return _record(
            "REG_NOT_FOUND", VerificationStatus.NOT_VERIFIED, SourceTier.OFFICIAL_REGULATOR, claim, _source(registry),
            f"{reg_no} was not found in the snapshot dated {registry.snapshot_date}.",
            "We couldn't find this number in SEBI's register. That doesn't mean it's fake (our copy may be out of "
            "date), but check it on sebi.gov.in before paying.",
            {"reg_no": reg_no, "snapshot_date": str(registry.snapshot_date)},
        )
    params = _entry_params(registry, entry)
    source, evidence = _source(registry, entry), _entry_evidence(entry)
    if entry.valid_till and entry.valid_till < today:
        return _record(
            "REG_EXPIRED", VerificationStatus.CONTRADICTED, SourceTier.OFFICIAL_REGULATOR, claim, source, evidence,
            f"This registration expired on {entry.valid_till.isoformat()}, so it is not currently valid.", params,
        )

    scores = [(n, entry.similarity(name_tokens(n))) for n in names]
    if any(s >= MATCH_THRESHOLD for _, s in scores):
        claimed = next(n for n, s in scores if s >= MATCH_THRESHOLD)
        return _record(
            "REG_NAME_MATCH", VerificationStatus.VERIFIED, SourceTier.OFFICIAL_REGULATOR,
            f"{claim} belongs to {claimed}", source, evidence,
            f"SEBI's register lists {reg_no} as {entry.name}, matching the name you were given. {IMPERSONATION_NOTE}",
            {**params, "claimed_name": claimed},
        )
    if scores and all(s <= DIFFERENT_THRESHOLD for _, s in scores):
        claimed = scores[0][0]
        return _record(
            "REG_NAME_MISMATCH", VerificationStatus.CONTRADICTED, SourceTier.OFFICIAL_REGULATOR,
            f"{claim} belongs to {claimed}", source, evidence,
            f"SEBI's register lists {reg_no} as {entry.name}, not {claimed}. Someone may be using another "
            "firm's registration number.",
            {**params, "claimed_name": claimed},
        )
    if scores:
        return _record(
            "REG_NAME_UNCLEAR", VerificationStatus.NOT_VERIFIED, SourceTier.OFFICIAL_REGULATOR,
            f"{claim} belongs to {scores[0][0]}", source, evidence,
            f"SEBI's register lists {reg_no} as {entry.name}. We can't tell for sure whether that is the name you "
            "were given; check it on sebi.gov.in.",
            {**params, "claimed_name": scores[0][0]},
        )
    # Registered, but we don't know which company the user was told about yet.
    return _record(
        "REG_NO_NAME", VerificationStatus.UNKNOWN, SourceTier.OFFICIAL_REGULATOR, claim, source, evidence,
        f"This number is registered to {entry.name}. Is that the company that contacted you?"
        + (f" (You mentioned {person_names[0]}; a person may work for a firm, so the firm name matters.)"
           if person_names else ""),
        params,
    )


def verify(facts: Facts | None, registry: Registry, today: date | None = None) -> list[VerificationRecord]:
    """Verification records for the current facts. Pure function: same facts + snapshot -> same records."""
    if facts is None:
        return []
    today = today or date.today()
    reg_entities = [e for e in facts.entities if e.type == "registration_number"]
    company_names = [e.value for e in facts.entities if e.type == "company"]
    person_names = [e.value for e in facts.entities if e.type == "person"]
    claims_registration = any(c.category == "registration" for c in facts.claims)
    offer = facts.offer_type

    records: list[VerificationRecord] = []
    for e in reg_entities:
        parsed = find_reg_numbers(e.value)
        well_formed = bool(parsed) and parsed[0].well_formed
        records.append(_check_reg_no(e.value.upper(), well_formed, company_names, person_names, registry, today))

    if reg_entities:
        return records

    if offer in NON_SEBI_OFFER_TYPES and not claims_registration:
        records.append(_record(
            "SEBI_NOT_APPLICABLE", VerificationStatus.NOT_APPLICABLE, SourceTier.OFFICIAL_REGULATOR,
            "SEBI registration", "Offer type", f"The offer looks like: {offer}.",
            "SEBI registration does not apply to this kind of offer. Check the points in the next steps instead.",
            {"offer_type": offer}, material=False,
        ))
        return records

    if claims_registration:
        records.append(_record(
            "REGISTRATION_CLAIM_NO_NUMBER", VerificationStatus.UNKNOWN, SourceTier.USER_PROVIDED,
            "Says they are SEBI registered", "What you were told",
            "A SEBI registration was claimed, but no registration number was given.",
            "They say they are SEBI registered, but we need the registration number to check it.", {},
        ))

    for name in company_names[:3]:
        if not registry.available:
            break
        found = registry.search_name(name)
        if found:
            entry, _ = found
            records.append(_record(
                "NAME_FOUND", VerificationStatus.VERIFIED, SourceTier.OFFICIAL_REGULATOR,
                f"{name} is SEBI registered", _source(registry, entry), _entry_evidence(entry),
                f"A firm named {entry.name} is on SEBI's register ({entry.reg_no}). {IMPERSONATION_NOTE}",
                {**_entry_params(registry, entry), "claimed_name": name},
            ))
        elif offer in SEBI_OFFER_TYPES or claims_registration:
            records.append(_record(
                "NAME_NOT_FOUND", VerificationStatus.NOT_VERIFIED, SourceTier.OFFICIAL_REGULATOR,
                f"{name} is SEBI registered", _source(registry),
                f"No clear match for {name} in the snapshot dated {registry.snapshot_date}.",
                "We couldn't find this name in SEBI's register. That doesn't mean it's fake, but anyone giving "
                "investment advice or tips for a fee must be SEBI registered. Ask for their registration number.",
                {"claimed_name": name, "snapshot_date": str(registry.snapshot_date)},
            ))
    return records

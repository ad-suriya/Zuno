"""SEBI registry snapshot loader (F08, ADR-010).

Reads `backend/data/sebi_registry.csv`, produced by `scripts/refresh_sebi.py` from SEBI's
public lists of registered intermediaries. Nothing calls SEBI during a request.
"""

import csv
import os
import re
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "sebi_registry.csv"

# Words that carry no identity: legal suffixes, honorifics and glue.
_DROP = {
    "pvt", "private", "ltd", "limited", "llp", "the", "and", "co", "company", "corp", "corporation", "inc",
    "india", "of", "ms", "m", "s", "mr", "mrs", "dr", "shri", "smt", "opc",
}
# Generic business words: shared by many firms, so they can't identify one on their own.
_GENERIC = {
    "capital", "wealth", "finance", "financial", "finserv", "securities", "investment", "investments", "advisor",
    "advisors", "adviser", "advisers", "advisory", "research", "broking", "brokers", "markets", "market", "trading",
    "services", "service", "consultants", "consultancy", "solutions", "global", "management", "stock", "stocks",
    "equity", "fund", "funds", "asset", "assets", "money", "group", "fintech", "ventures", "holdings", "partners",
}

MATCH_THRESHOLD = 0.8
DIFFERENT_THRESHOLD = 0.25


def name_tokens(name: str) -> frozenset[str]:
    text = name.lower().replace("&", " and ")
    text = re.sub(r"[^\w\s]", " ", text)
    return frozenset(t for t in text.split() if t not in _DROP)


def name_similarity(a: frozenset[str], b: frozenset[str]) -> float:
    """Token-set similarity in [0, 1]. A subset match on distinctive words counts as a strong match."""
    if not a or not b:
        return 0.0
    jaccard = len(a & b) / len(a | b)
    small, big = (a, b) if len(a) <= len(b) else (b, a)
    distinctive = small - _GENERIC
    if distinctive and small <= big and any(len(t) >= 3 for t in distinctive):
        return max(jaccard, 0.85)
    return jaccard


@dataclass(frozen=True)
class RegistryEntry:
    reg_no: str
    name: str
    trade_name: str
    category: str
    valid_from: date | None
    valid_till: date | None  # None = perpetual
    snapshot_date: date
    source_url: str
    tokens: frozenset[str] = field(default=frozenset(), compare=False)
    trade_tokens: frozenset[str] = field(default=frozenset(), compare=False)

    def similarity(self, tokens: frozenset[str]) -> float:
        return max(name_similarity(tokens, self.tokens), name_similarity(tokens, self.trade_tokens))


class Registry:
    def __init__(self, entries: list[RegistryEntry]):
        self.entries = entries
        self.by_reg_no = {e.reg_no: e for e in entries}
        self.prefixes = {e.reg_no[:3] for e in entries}
        self.snapshot_date: date | None = max((e.snapshot_date for e in entries), default=None)

    @property
    def available(self) -> bool:
        return bool(self.entries)

    def lookup(self, reg_no: str) -> RegistryEntry | None:
        return self.by_reg_no.get(reg_no.upper())

    def search_name(self, name: str) -> tuple[RegistryEntry, float] | None:
        """Best match at or above MATCH_THRESHOLD; ties (ambiguous names) return None."""
        tokens = name_tokens(name)
        if not tokens - _GENERIC:
            return None
        scored = [(e, e.similarity(tokens)) for e in self.entries]
        best = [s for s in scored if s[1] >= MATCH_THRESHOLD]
        if not best:
            return None
        best.sort(key=lambda s: (-s[1], s[0].reg_no))
        top_score = best[0][1]
        top = [s for s in best if s[1] == top_score]
        distinct = {e.name.lower() for e, _ in top}
        return best[0] if len(distinct) == 1 else None


def _date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def load_registry(path: Path | str | None = None) -> Registry:
    path = Path(path or os.environ.get("SEBI_REGISTRY_PATH") or DEFAULT_PATH)
    if not path.is_file():
        return Registry([])
    entries = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            entries.append(
                RegistryEntry(
                    reg_no=row["reg_no"].upper(),
                    name=row["name"],
                    trade_name=row.get("trade_name", ""),
                    category=row["category"],
                    valid_from=_date(row.get("valid_from", "")),
                    valid_till=_date(row.get("valid_till", "")),
                    snapshot_date=date.fromisoformat(row["snapshot_date"]),
                    source_url=row.get("source_url", ""),
                    tokens=name_tokens(row["name"]),
                    trade_tokens=name_tokens(row.get("trade_name", "")),
                )
            )
    return Registry(entries)


@lru_cache
def get_registry() -> Registry:
    return load_registry()

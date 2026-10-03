#!/usr/bin/env python3
"""Download SEBI's public lists of registered intermediaries into a dated offline snapshot (ADR-010).

    python3 scripts/refresh_sebi.py            # writes backend/data/sebi_registry.csv

Only the standard library is used. The snapshot is read by the verification engine
(backend/app/engine/registry.py); nothing calls SEBI while handling a user request.
Source: https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=<id>
"""

import csv
import html
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from http.cookiejar import CookieJar
from pathlib import Path

BASE = "https://www.sebi.gov.in"
LIST_URL = BASE + "/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId={intm_id}"
PAGE_URL = BASE + "/sebiweb/ajax/other/getintmfpiinfo.jsp"

# SEBI intermediary type id -> category stored in the snapshot.
# Start with the categories most impersonated in tip/advisory scams (docs/plan/08-verification-sebi.md).
CATEGORIES = {
    13: "Investment Adviser",
    14: "Research Analyst",
    30: "Stock Broker",
}

OUT = Path(__file__).resolve().parents[1] / "backend" / "data" / "sebi_registry.csv"
FIELDS = ["reg_no", "name", "trade_name", "category", "valid_from", "valid_till", "snapshot_date", "source_url"]

_PAIR = re.compile(r"""<div class=["']title["']><span>([^<]+)</span></div><div class=["']value[^"']*["']><span>([^<]*)</span>""")
_TOTAL_RECORDS = re.compile(r"of (\d+) records")
_PAGE_SIZE = 25
_DELAY_S = 0.5  # be polite to sebi.gov.in
_RETRIES = 6


def _opener() -> urllib.request.OpenerDirector:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Zuno SEBI snapshot; contact: team Caffeine Overflow)")]
    return opener


def _get(opener, url: str, data: dict | None = None, referer: str | None = None) -> str:
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body)
    if referer:
        req.add_header("Referer", referer)
        req.add_header("X-Requested-With", "XMLHttpRequest")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    for attempt in range(_RETRIES):
        try:
            with opener.open(req, timeout=60) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except OSError as exc:
            if attempt == _RETRIES - 1:
                raise
            print(f"  retrying after {type(exc).__name__}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def _date(text: str) -> str:
    text = text.strip()
    try:
        return datetime.strptime(text, "%b %d, %Y").date().isoformat()
    except ValueError:
        return ""  # "Perpetual" or blank


def parse_records(page: str) -> list[dict[str, str]]:
    """Each record is a run of title/value pairs starting with "Name"."""
    records: list[dict[str, str]] = []
    for title, value in _PAIR.findall(page):
        title, value = title.strip(), html.unescape(value).strip()
        if title == "Name":
            records.append({})
        if records:
            records[-1][title] = value
    return records


def _row(rec: dict[str, str], category: str, source_url: str, snapshot: str) -> dict[str, str] | None:
    reg_no = re.sub(r"\s+", "", rec.get("Registration No.", "")).upper()
    name = re.sub(r"\s+", " ", rec.get("Name", "")).strip()
    if not reg_no or not name:
        return None
    valid_from, _, valid_till = rec.get("Validity", "").partition(" - ")
    return {
        "reg_no": reg_no,
        "name": name,
        "trade_name": re.sub(r"\s+", " ", rec.get("Trade Name", "")).strip(),
        "category": category,
        "valid_from": _date(valid_from),
        "valid_till": _date(valid_till),  # empty = perpetual
        "snapshot_date": snapshot,
        "source_url": source_url,
    }


def fetch_category(intm_id: int, category: str, snapshot: str) -> list[dict[str, str]]:
    opener = _opener()
    url = LIST_URL.format(intm_id=intm_id)
    first = _get(opener, url)
    m = _TOTAL_RECORDS.search(first)
    expected = int(m.group(1)) if m else None
    total_pages = -(-expected // _PAGE_SIZE) if expected else 1
    records = parse_records(first)
    for page in range(1, total_pages):
        time.sleep(_DELAY_S)
        form = {
            "nextValue": "1", "next": "n", "intmId": str(intm_id), "contPer": "", "name": "", "regNo": "",
            "email": "", "location": "", "exchange": "", "affiliate": "", "alp": "", "language": "2",
            "model": "", "esgCategory": "", "doDirect": str(page), "intmIds": "",
        }
        records += parse_records(_get(opener, PAGE_URL, form, referer=url))
        print(f"  {category}: page {page + 1}/{total_pages}", file=sys.stderr, end="\r")
    rows = [r for rec in records if (r := _row(rec, category, url, snapshot))]
    print(f"  {category}: {len(rows)} records (SEBI reports {expected})", file=sys.stderr)
    return rows


def main() -> None:
    snapshot = date.today().isoformat()
    rows: dict[str, dict[str, str]] = {}
    for intm_id, category in CATEGORIES.items():
        for row in fetch_category(intm_id, category, snapshot):
            rows.setdefault(row["reg_no"], row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows.values(), key=lambda r: r["reg_no"]))
    print(f"Wrote {len(rows)} records to {OUT} (snapshot {snapshot})", file=sys.stderr)


if __name__ == "__main__":
    main()

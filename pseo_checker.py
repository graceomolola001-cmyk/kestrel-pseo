#!/usr/bin/env python3
"""
pSEO dataset checker (v3).

Usage:
    python pseo_checker.py data/pages.csv

Columns (lowercase headers):
    programme, country, fees, duration, entry, intake, suits,
    source, last_verified, status

status must be "publish" or "hold". Held rows are not checked and are
not built.

Levels:
    FIX     do not publish until resolved (the build refuses to run)
    REVIEW  a person must confirm this against the source
    HOLD    row is held back (information only)

Exit code is 1 if any FIX exists, otherwise 0.
Standard library only. This tool finds patterns. It cannot tell you
whether a fact is TRUE: only the source can.
"""
import csv
import re
import sys
from collections import Counter
from datetime import date, datetime

REQUIRED_COLUMNS = ["programme", "country", "fees", "duration", "entry",
                    "intake", "suits", "source", "last_verified", "status"]
FACT_COLUMNS = ["fees", "duration", "entry", "intake", "suits", "source",
                "last_verified"]

# Edit for your countries. Verify codes against ISO 4217.
CURRENCY_BY_COUNTRY = {
    "zambia": "ZMW", "ghana": "GHS", "uganda": "UGX",
    "nigeria": "NGN", "malawi": "MWK",
}
STALE_AFTER_DAYS = 180
REPEAT_SHARE_LIMIT = 0.5
VALID_STATUS = ("publish", "hold")


def clean(v):
    return (v or "").strip()


def norm(v):
    return re.sub(r"\s+", " ", clean(v).lower())


def status_of(r):
    return clean(r.get("status")).lower()


def check(rows, today=None):
    today = today or date.today()
    out = []  # (level, where, message)

    def lab(i, r):
        return f"row {i} ({clean(r.get('programme'))} / {clean(r.get('country'))})"

    numbered = list(enumerate(rows, start=2))  # row 1 is the header

    # status and duplicate keys apply to every row
    seen_key = {}
    for i, r in numbered:
        if status_of(r) not in VALID_STATUS:
            out.append(("FIX", lab(i, r),
                        f"status '{clean(r.get('status'))}' must be publish or hold"))
        key = (norm(r.get("programme")), norm(r.get("country")))
        if key in seen_key:
            out.append(("FIX", lab(i, r),
                        f"same programme and country as row {seen_key[key]}"))
        else:
            seen_key[key] = i

    active = [(i, r) for i, r in numbered if status_of(r) == "publish"]
    for i, r in numbered:
        if status_of(r) == "hold":
            out.append(("HOLD", lab(i, r), "held back, not checked and not built"))

    for i, r in active:
        blanks = [c for c in FACT_COLUMNS if not clean(r.get(c))]
        if blanks:
            out.append(("FIX", lab(i, r), "blank: " + ", ".join(blanks)))

        fees = clean(r.get("fees"))
        country = norm(r.get("country"))
        expected = CURRENCY_BY_COUNTRY.get(country)
        if fees and expected and not fees.upper().startswith(expected + " "):
            out.append(("FIX", lab(i, r),
                        f"fees '{fees}' should start with {expected}"))
        if fees and not expected:
            out.append(("REVIEW", lab(i, r),
                        f"no currency rule for country '{country}'"))

        dur = clean(r.get("duration"))
        if dur and not re.fullmatch(r"\d+ months", dur):
            out.append(("REVIEW", lab(i, r),
                        f"duration '{dur}' is not in the form '24 months'"))

        intake = clean(r.get("intake"))
        if intake and not re.search(r"\b(19|20)\d{2}\b", intake):
            out.append(("REVIEW", lab(i, r), f"intake '{intake}' has no year"))

        lv = clean(r.get("last_verified"))
        if lv:
            try:
                d = datetime.strptime(lv, "%Y-%m-%d").date()
                if d > today:
                    out.append(("FIX", lab(i, r), f"last_verified {lv} is in the future"))
                elif (today - d).days > STALE_AFTER_DAYS:
                    out.append(("REVIEW", lab(i, r),
                                f"last_verified {lv} is older than {STALE_AFTER_DAYS} days"))
            except ValueError:
                out.append(("FIX", lab(i, r), f"last_verified '{lv}' is not YYYY-MM-DD"))

    n = len(active)
    if n >= 4:
        counts = Counter(norm(r.get("entry")) for _, r in active if clean(r.get("entry")))
        for value, k in counts.items():
            if k / n > REPEAT_SHARE_LIMIT:
                out.append(("REVIEW", "column 'entry'",
                            f"one value appears in {k} of {n} rows: '{value}'"))

    seen_suits, seen_facts = {}, {}
    for i, r in active:
        s = norm(r.get("suits"))
        if s:
            if s in seen_suits:
                out.append(("REVIEW", lab(i, r),
                            f"suits text is identical to row {seen_suits[s]}"))
            else:
                seen_suits[s] = i
        key = tuple(norm(r.get(c)) for c in ("fees", "duration", "entry", "intake"))
        if all(key):
            if key in seen_facts:
                out.append(("REVIEW", lab(i, r),
                            f"same fees, duration, entry and intake as row {seen_facts[key]}"))
            else:
                seen_facts[key] = i
    return out


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = [h.strip().lower() for h in (reader.fieldnames or [])]
        missing = [c for c in REQUIRED_COLUMNS if c not in headers]
        if missing:
            return None, missing
        rows = [{(k or "").strip().lower(): v for k, v in r.items()} for r in reader]
    return rows, []


def main(path):
    rows, missing = load(path)
    if missing:
        print("FIX    missing columns: " + ", ".join(missing))
        return 1
    findings = check(rows)
    for level, where, msg in findings:
        print(f"{level:<7}{where}: {msg}")
    fix = sum(1 for f in findings if f[0] == "FIX")
    rev = sum(1 for f in findings if f[0] == "REVIEW")
    hold = sum(1 for f in findings if f[0] == "HOLD")
    print(f"\n{len(rows)} rows read. {fix} FIX, {rev} REVIEW, {hold} held.")
    return 1 if fix else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

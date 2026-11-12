#!/usr/bin/env python3
"""
Fix dataset values that disagree with data/sources.md.

Usage:
    python fix_from_sources.py            DRY RUN: show what would change, write nothing
    python fix_from_sources.py --apply    make the changes (a backup is saved first)

What it does
  * For fees, duration, intake and entry: if a row's value differs from the
    source table, the source value wins.
  * If all four of those now match the source, it fills a blank `source` and
    sets `last_verified` to the date written in sources.md.
  * It writes every change to step1-changes.md so you can review it.

What it does NOT do
  * It never edits the `suits` text. That is editorial copy with no source.
    Duplicates are reported for a person to rewrite.
  * It never guesses. A row with no match in sources.md is reported and skipped.
  * It is only as good as sources.md. Read the dry run before you apply.

Standard library only.
"""
import csv
import os
import re
import shutil
import sys
from datetime import datetime

CSV_PATH = os.path.join("data", "pages.csv")
SRC_PATH = os.path.join("data", "sources.md")
LOG_PATH = "step1-changes.md"
SOURCE_LABEL = "Fee schedule 2026-27; Admissions handbook 2026"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_sources(path):
    truth, verified, section = {}, None, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.search(r"verified on \*\*(\d{4}-\d{2}-\d{2})\*\*", line)
            if m:
                verified = m.group(1)
            if line.startswith("## "):
                low = line.lower()
                section = "fees" if "fee schedule" in low else "entry" if "admissions" in low else None
                continue
            if not line.startswith("|") or section is None:
                continue
            c = cells(line)
            if c[0] == "Programme" or set(c[0]) <= set("-: "):
                continue
            key = (c[0].lower(), c[1].lower())
            rec = truth.setdefault(key, {})
            if section == "fees" and len(c) >= 5:
                rec.update(fees=c[2], duration=c[3], intake=c[4])
            elif section == "entry" and len(c) >= 3:
                rec["entry"] = c[2]
    return truth, verified


def main(apply):
    for p in (CSV_PATH, SRC_PATH):
        if not os.path.isfile(p):
            print(f"Cannot find {p}. Run this from the kestrel-pseo folder.")
            return 1
    truth, verified = parse_sources(SRC_PATH)
    if not truth or not verified:
        print("Could not read sources.md (no tables or no verified date found).")
        return 1

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    changes, skipped = [], []
    for n, r in enumerate(rows, start=2):
        who = f"{r['programme']} / {r['country']}"
        t = truth.get((r["programme"].strip().lower(), r["country"].strip().lower()))
        if not t or any(k not in t for k in ("fees", "duration", "intake", "entry")):
            skipped.append(f"row {n} ({who}): no complete match in sources.md, left alone")
            continue
        for k in ("fees", "duration", "intake", "entry"):
            if r[k].strip() != t[k]:
                changes.append((n, who, k, r[k], t[k], "source table says so"))
                r[k] = t[k]
        if all(r[k].strip() == t[k] for k in ("fees", "duration", "intake", "entry")):
            if not r["source"].strip():
                changes.append((n, who, "source", r["source"], SOURCE_LABEL, "facts match the source documents"))
                r["source"] = SOURCE_LABEL
            if r["last_verified"].strip() != verified:
                changes.append((n, who, "last_verified", r["last_verified"], verified, "sources.md verification date"))
                r["last_verified"] = verified

    seen, human = {}, []
    for n, r in enumerate(rows, start=2):
        if r["status"].strip().lower() != "publish":
            continue
        s = re.sub(r"\s+", " ", r["suits"].strip().lower())
        if s and s in seen:
            human.append(f"row {n} ({r['programme']} / {r['country']}): 'suits' text is identical to row {seen[s]}. "
                         "Write a new sentence for this row, or set status to hold.")
        elif s:
            seen[s] = n

    print(("APPLYING" if apply else "DRY RUN (nothing written)") + "\n")
    for n, who, k, old, new, why in changes:
        print(f"row {n} ({who}) {k}: '{old}' -> '{new}'")
    if not changes:
        print("No source-backed changes needed.")
    for s in skipped:
        print("SKIPPED " + s)
    for h in human:
        print("NEEDS A PERSON " + h)
    print(f"\n{len(changes)} change(s). {len(skipped)} skipped. {len(human)} need a person.")

    if apply and changes:
        backup = CSV_PATH.replace(".csv", ".backup.csv")
        if os.path.exists(backup):
            backup = CSV_PATH.replace(".csv", f".backup-{datetime.now():%H%M%S}.csv")
        shutil.copy(CSV_PATH, backup)
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("# Changes made by fix_from_sources.py\n\n")
            f.write("| Row | Page | Field | Was | Now | Reason |\n|---|---|---|---|---|---|\n")
            for n, who, k, old, new, why in changes:
                f.write(f"| {n} | {who} | {k} | {old or '(blank)'} | {new} | {why} |\n")
            f.write("\nAdd your own notes: what the checker said, and anything you decided by hand.\n")
        print(f"Backup saved to {backup}. Change log written to {LOG_PATH}.")
        print("Now run: python pseo_checker.py data/pages.csv")
    elif not apply and changes:
        print("Read the list above. If every change matches the source, run again with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv[1:]))
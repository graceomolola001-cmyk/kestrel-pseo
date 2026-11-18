"""Generate and validate a private, synthetic programmatic SEO scale test.

This uses the SAME CSV -> build.py -> qa.py -> SEO audit pipeline as the
public Kestrel website. The 500 stress-test pages are NOT deployed publicly.
Every record is labeled as invented. No Google APIs or credentials are used.

Usage:
    python -m seo_ops.scale_test --count 500
    python -m seo_ops.scale_test --count 8 --out reports/small-scale-test
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from .core import audit_directory, audit_html

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["programme", "country", "fees", "duration", "entry", "intake",
          "suits", "source", "last_verified", "status"]
MARKETS = [
    ("Nigeria", "NGN"), ("Ghana", "GHS"),
    ("Zambia", "ZMW"), ("Malawi", "MWK"),
]
BASE = "http://localhost:8000"  # local preview uses the site directory as web root


def fixture_rows(count: int):
    """Create unique, explicit test records, never real programme claims."""
    if not 1 <= count <= 5000:
        raise ValueError("count must be between 1 and 5000")
    out = []
    for i in range(count):
        number = i + 1
        country, currency = MARKETS[i % len(MARKETS)]
        programme = f"Scale Test Topic {i // len(MARKETS) + 1:04d}"
        out.append({
            "programme": programme,
            "country": country,
            "fees": f"{currency} {10000 + number * 3:,}",
            "duration": f"{(12,18,24,30)[i % 4]} months",
            "entry": f"Fictional eligibility rule {i % 9 + 1}",
            "intake": "January 2027",
            "suits": f"Synthetic audience group {number:04d}, only for automation testing.",
            "source": f"GENERATED TEST FIXTURE {number:04d}; never publish as real course facts",
            "last_verified": date.today().isoformat(),
            "status": "publish",
        })
    return out


def run(count=500, output="reports/scale-test"):
    target = Path(output).resolve()
    # Prevent a wrong output path from wiping source files or the live dist/.
    if target == ROOT or ROOT in target.parents and target == ROOT / "dist":
        raise ValueError("Never run this scale test against the public dist folder")
    target.mkdir(parents=True, exist_ok=True)
    csv_file = target / "generated-records.csv"
    site_dir = target / "site"
    records = fixture_rows(count)
    with csv_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)

    commands = [
        [sys.executable, "build.py", "--csv", str(csv_file),
         "--out", str(site_dir), "--base-url", BASE],
        [sys.executable, "qa.py", str(site_dir)],
    ]
    times = {}
    for name, command in zip(("build_seconds", "qa_seconds"), commands):
        started = perf_counter()
        result = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, check=False
        )
        times[name] = round(perf_counter() - started, 3)
        if result.returncode:
            print(result.stdout[-6000:], file=sys.stderr)
            print(result.stderr[-3000:], file=sys.stderr)
            raise RuntimeError(f"{name} returned status {result.returncode}")
        print(f"PASS {name}: {result.stdout.splitlines()[-1] if result.stdout else 'complete'}")

    started = perf_counter()
    report = audit_directory(site_dir, BASE)
    times["audit_seconds"] = round(perf_counter() - started, 3)
    if report["status"] != "pass":
        raise RuntimeError(f"SEO audit found {report['counts']['error']} errors")
    expected_pages = count + 5  # home, course list, systems, lab, reports
    actual_pages = report["pages_checked"]
    if actual_pages != expected_pages:
        raise RuntimeError(f"Expected {expected_pages} HTML pages, got {actual_pages}")

    # Explicitly prove real, unique URLs and noindex signals.
    html_files = list(site_dir.rglob("*.html"))
    canonicals = []
    for file in html_files:
        html = file.read_text(encoding="utf-8")
        if '<meta name="robots" content="noindex, nofollow">' not in html:
            raise RuntimeError(f"Index safety rule missing on {file}")
        start = html.find('<link rel="canonical" href="')
        if start < 0:
            raise RuntimeError(f"Canonical missing on {file}")
        start += len('<link rel="canonical" href="')
        canonicals.append(html[start:html.index('"', start)])
    if len(set(canonicals)) != len(canonicals):
        raise RuntimeError("Duplicate canonical URLs in scale-test site")

    # An intentional, LOCAL experiment. Never treat this as a live incident.
    first_page = next((site_dir / "programmes").glob("*/index.html"))
    first_html = first_page.read_text(encoding="utf-8")
    # This single test asks what happens if a noindex page were expected to be indexable.
    canonical_tag = '<link rel="canonical" href="'
    canonical_start = first_html.index(canonical_tag) + len(canonical_tag)
    actual_canonical = first_html[canonical_start:first_html.index('"', canonical_start)]
    injected, _ = audit_html(first_html, actual_canonical, expect_indexable=True)
    codes = [x.code for x in injected]
    if "UNEXPECTED_NOINDEX" not in codes:
        raise RuntimeError("Expected the injected indexability failure to be detected")

    summary = {
        "dataset": "SYNTHETIC TEST DATA ONLY",
        "publicly_deployed": False,
        "requested_generated_records": count,
        "generated_programme_pages": count,
        "html_pages_checked": actual_pages,
        "unique_canonicals": len(set(canonicals)),
        "seo_errors": report["counts"]["error"],
        "seo_warnings": report["counts"]["warning"],
        "qa_exit_status": "PASS",
        "fault_injection": {
            "type": "indexability baseline mismatch",
            "live_incident": False,
            "detected_issue_codes": codes
        },
        "timings_seconds": times,
    }
    for name, data in (("summary.json", summary), ("seo-audit.json", report)):
        (target / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="timings_seconds"}, indent=2))
    print(f"Detailed reports: {target}")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate 500 fictional Kestrel pSEO pages offline")
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--out", default="reports/scale-test")
    args = parser.parse_args(argv)
    run(count=args.count, output=args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

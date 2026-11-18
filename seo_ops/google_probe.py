"""Read-only smoke tests for real Kestrel Google APIs.

Usage (from repository root):
    python -m seo_ops.google_probe

Authentication: Google Application Default Credentials.
Set GOOGLE_APPLICATION_CREDENTIALS to a private service-account JSON path.
Never save credentials in Git, issue comments, workflow logs, or chat.
"""
from __future__ import annotations
import argparse
from datetime import date, timedelta
import sys

SITE = "https://graceomolola001-cmyk.github.io/kestrel-pseo/"
GA4_PROPERTY = "565038230"


def _check_gsc(site_property: str) -> int:
    from .google_data import _session, query_gsc
    session = _session()
    response = session.get("https://www.googleapis.com/webmasters/v3/sites", timeout=30)
    response.raise_for_status()
    sites = {x.get("siteUrl") for x in response.json().get("siteEntry", [])}
    found = site_property in sites
    print(f"GSC: API authentication successful; requested property accessible: {'YES' if found else 'NO'}")
    if not found:
        print("      Confirm that the service-account email has access to the exact URL-prefix property.")
        return 2
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=6)
    rows = query_gsc(site_property, start.isoformat(), end.isoformat())
    print(f"GSC: Search Analytics query successful; {len(rows)} page rows (last 7 complete days ending {end}).")
    if not rows:
        print("      No search rows is expected for a new, noindex demo; authentication still passed.")
    return 0


def _check_ga4(property_id: str) -> int:
    from .google_data import query_ga4
    end = date.today()
    start = end - timedelta(days=6)
    rows = query_ga4(property_id, start.isoformat(), end.isoformat())
    print(f"GA4: Data API authentication successful; {len(rows)} daily report rows ({start} to {end}).")
    if rows:
        total_sessions = sum(int(float(r.get("sessions", 0))) for r in rows)
        total_key_events = sum(float(r.get("key_events", 0)) for r in rows)
        print(f"GA4: {total_sessions} reported sessions; {total_key_events:g} reported key events in this date range.")
        print("     Key events are configured in GA4; do not treat them as verified CRM signups.")
    else:
        print("     The API returned an empty report; check date range and property data in GA4.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify Kestrel's read-only GA4 and GSC API connections")
    parser.add_argument("--ga4-property", default=GA4_PROPERTY)
    parser.add_argument("--gsc-property", default=SITE)
    parser.add_argument("--only", choices=("ga4", "gsc", "both"), default="both")
    args = parser.parse_args(argv)

    if not args.ga4_property.isdigit():
        parser.error("The GA4 property is a numeric ID such as 565038230")
    if not args.gsc_property.startswith("https://"):
        parser.error("The GSC property must be the exact HTTPS URL-prefix property")

    try:
        import google.auth  # noqa: F401
        import requests  # noqa: F401
    except ImportError:
        print("Install optional dependencies: python -m pip install -r seo_ops/requirements-optional.txt", file=sys.stderr)
        return 2

    tasks = []
    if args.only in ("both", "ga4"):
        tasks.append(("GA4", lambda: _check_ga4(args.ga4_property)))
    if args.only in ("both", "gsc"):
        tasks.append(("GSC", lambda: _check_gsc(args.gsc_property)))
    failures = 0
    for label, task in tasks:
        try:
            result = task()
            failures += result != 0
        except Exception as exc:
            # Never print a credential JSON or access token in diagnostics.
            code = getattr(getattr(exc, "response", None), "status_code", None)
            if code in (401, 403):
                detail = "Authorization failed. Check enabled APIs and property-level service account access."
            elif code == 404:
                detail = "Property or API endpoint not found. Check the exact property ID and enabled API."
            elif code == 429:
                detail = "Google API rate limit reached. Retry later."
            else:
                detail = "The request could not complete. Confirm credentials and network access."
            print(f"{label}: FAILED. {detail}", file=sys.stderr)
            failures += 1
    print("Connection check: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

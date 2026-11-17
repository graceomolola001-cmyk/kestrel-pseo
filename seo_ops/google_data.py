"""Optional read-only Google APIs; requires google-auth and property access.

No data is fabricated when credentials are absent. Never commit credentials.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

SCOPE = ['https://www.googleapis.com/auth/webmasters.readonly',
         'https://www.googleapis.com/auth/analytics.readonly']


def _session():
    try:
        import google.auth
        from google.auth.transport.requests import AuthorizedSession
    except ImportError as exc:
        raise RuntimeError('Install optional dependencies: pip install -r seo_ops/requirements-optional.txt') from exc
    credentials, _ = google.auth.default(scopes=SCOPE)
    return AuthorizedSession(credentials)


def query_gsc(site_property: str, start: str, end: str):
    """Read page-level search performance (top rows, not exhaustive)."""
    session = _session()
    url = f'https://www.googleapis.com/webmasters/v3/sites/{quote(site_property, safe="")}/searchAnalytics/query'
    response = session.post(url, json={'startDate': start, 'endDate': end,
                                        'dimensions': ['page'], 'rowLimit': 25000}, timeout=30)
    response.raise_for_status()
    return [{'page': r['keys'][0], 'clicks': r['clicks'],
             'impressions': r['impressions'], 'ctr': r['ctr'], 'position': r['position']}
            for r in response.json().get('rows', [])]


def query_ga4(property_id: str, start: str, end: str):
    """Read daily sessions and key events through the GA4 Data API."""
    session = _session()
    url = f'https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport'
    body = {'dateRanges': [{'startDate': start, 'endDate': end}],
            'dimensions': [{'name': 'date'}],
            'metrics': [{'name': 'sessions'}, {'name': 'keyEvents'}], 'limit': 10000}
    response = session.post(url, json=body, timeout=30)
    response.raise_for_status()
    return [{'date': r['dimensionValues'][0]['value'],
             'sessions': r['metricValues'][0]['value'],
             'key_events': r['metricValues'][1]['value']}
            for r in response.json().get('rows', [])]


def save_csv(rows: list[dict], output: str, fieldnames: list[str]):
    path = Path(output); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as output_handle:
        writer = csv.DictWriter(output_handle, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(rows)


def default_dates():
    end = date.today() - timedelta(days=3)  # avoid reporting very recent incomplete GSC data
    start = end - timedelta(days=27)
    return start.isoformat(), end.isoformat()

"""Prioritize content reviews with Search Console performance data.
Human review remains required before publishing.
"""
import csv
from pathlib import Path


def create_refresh_queue(input_csv: str, output_csv: str, min_impressions=100):
    results = []
    with open(input_csv, newline='', encoding='utf-8-sig') as handle:
        for row in csv.DictReader(handle):
            impressions = float(row.get('impressions', 0))
            ctr = float(row.get('ctr', 0))
            position = float(row.get('position', 100))
            if impressions < min_impressions:
                continue
            reasons = []
            if 4 <= position <= 20:
                reasons.append('Position 4-20: investigate on-page and internal links')
            if ctr < .03:
                reasons.append('CTR below 3%: review title/snippet and intent')
            if not reasons:
                continue
            opportunity_score = impressions * max(0, .05 - ctr) * (1 if position <= 20 else .25)
            results.append({'page': row['page'], 'impressions': int(impressions),
                            'clicks': row.get('clicks',''), 'ctr': round(ctr,4),
                            'position': round(position,2), 'priority_score': round(opportunity_score,2),
                            'review_reasons': '; '.join(reasons), 'approval': 'PENDING_HUMAN_REVIEW'})
    results.sort(key=lambda x: x['priority_score'], reverse=True)
    path = Path(output_csv); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        columns = ['page','impressions','clicks','ctr','position','priority_score','review_reasons','approval']
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader(); writer.writerows(results)
    return results

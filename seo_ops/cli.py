"""Entry point for local CI, live auditing, redirects, GSC / GA4 and experiments."""
import argparse
import json
import os
import sys

from .core import audit_directory, validate_redirect_map
from .crawler import crawl
from .experiments import evaluate, plan_sample_size
from .refresh import create_refresh_queue
from .reporting import notify, save_report


def _write_and_exit(report, args):
    save_report(report, args.out, getattr(args, 'html', None))
    print(f'{report["mode"].upper()}: {report["pages_checked"]} URLs, {report["counts"]["error"]} errors, {report["counts"]["warning"]} warnings. Report: {args.out}')
    if getattr(args, 'notify', False):
        try:
            notify(report)
        except Exception as exc:
            print(f'Notification failed: {exc}', file=sys.stderr)
    return 1 if getattr(args, 'strict', False) and report['status'] == 'fail' else 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog='python -m seo_ops.cli', description='Reproducible SEO engineering checks')
    sub = parser.add_subparsers(dest='command', required=True)
    directory = sub.add_parser('audit-dir', help='Audit generated HTML before publishing')
    directory.add_argument('directory')
    directory.add_argument('--base-url', required=True)
    directory.add_argument('--expect-indexable', action='store_true')
    directory.add_argument('--require-schema', action='store_true')
    directory.add_argument('--out', default='reports/site-audit.json')
    directory.add_argument('--html')
    directory.add_argument('--strict', action='store_true')

    live = sub.add_parser('crawl', help='Bounded, robots-aware live site crawl')
    live.add_argument('--url', required=True)
    live.add_argument('--max-pages', type=int, default=30)
    live.add_argument('--delay', type=float, default=.3)
    live.add_argument('--expect-indexable', action='store_true')
    live.add_argument('--require-schema', action='store_true')
    live.add_argument('--out', default='reports/live-audit.json')
    live.add_argument('--html')
    live.add_argument('--strict', action='store_true')
    live.add_argument('--notify', action='store_true')

    redirects = sub.add_parser('redirects', help='Check redirect CSV for duplicates, cycles, chains')
    redirects.add_argument('csv')
    redirects.add_argument('--out', default='reports/redirect-audit.json')
    redirects.add_argument('--strict', action='store_true')

    experiment = sub.add_parser('experiment', help='Evaluate a preregistered, fixed-horizon A/B test')
    experiment.add_argument('input', help='JSON with baseline_rate, relative_mde, hypothesis, visitors and conversions')

    refresh = sub.add_parser('refresh-queue', help='Queue content opportunities from GSC page-level CSV')
    refresh.add_argument('--input', required=True)
    refresh.add_argument('--output', default='reports/refresh-queue.csv')
    refresh.add_argument('--min-impressions', type=int, default=100)

    google = sub.add_parser('google-pull', help='Optional read-only GSC / GA4 API exports')
    google.add_argument('--gsc-property', help='Exact URL-prefix or sc-domain: property identifier')
    google.add_argument('--ga4-property', help='GA4 property numeric ID')
    google.add_argument('--start-date')
    google.add_argument('--end-date')
    google.add_argument('--output-dir', default='reports')

    args = parser.parse_args(argv)
    if args.command == 'audit-dir':
        report = audit_directory(args.directory, args.base_url, args.expect_indexable, args.require_schema)
        return _write_and_exit(report, args)
    if args.command == 'crawl':
        if not 1 <= args.max_pages <= 500 or not 0 <= args.delay <= 60:
            parser.error('max-pages must be 1-500, delay 0-60 seconds')
        return _write_and_exit(crawl(args.url, args.max_pages, args.delay, args.expect_indexable, args.require_schema), args)
    if args.command == 'redirects':
        return _write_and_exit(validate_redirect_map(args.csv), args)
    if args.command == 'experiment':
        with open(args.input, encoding='utf-8') as handle:
            data = json.load(handle)
        n = plan_sample_size(data['baseline_rate'], data['relative_mde'], data.get('power',.8), data.get('alpha',.05))
        result = {'hypothesis':data['hypothesis'], 'planned_min_per_arm': n,
                  'pre_registered':data.get('pre_registered', False),
                  'sample_dataset': data.get('sample_dataset', 'unlabeled')}
        if not result['pre_registered']:
            result['warning'] = 'No pre-registration evidence: this does not establish an authentic experiment.'
        if all(k in data for k in ('control_visitors','control_conversions','variant_visitors','variant_conversions')):
            result.update(evaluate(data['control_visitors'],data['control_conversions'],data['variant_visitors'],data['variant_conversions'],n,data.get('alpha',.05)))
        print(json.dumps(result, indent=2))
        return 0
    if args.command == 'refresh-queue':
        queue = create_refresh_queue(args.input, args.output, args.min_impressions)
        print(f'{len(queue)} pages queued for human review: {args.output}')
        return 0
    if args.command == 'google-pull':
        from .google_data import default_dates, query_ga4, query_gsc, save_csv
        if not args.gsc_property and not args.ga4_property:
            parser.error('Supply --gsc-property and/or --ga4-property')
        start, end = default_dates(); start = args.start_date or start; end = args.end_date or end
        if args.gsc_property:
            rows = query_gsc(args.gsc_property, start, end)
            save_csv(rows, os.path.join(args.output_dir, 'gsc-pages.csv'), ['page','clicks','impressions','ctr','position'])
            print(f'GSC export: {len(rows)} top page rows; {start} to {end}')
        if args.ga4_property:
            rows = query_ga4(args.ga4_property, start, end)
            save_csv(rows, os.path.join(args.output_dir,'ga4-daily.csv'), ['date','sessions','key_events'])
            print(f'GA4 export: {len(rows)} daily rows; {start} to {end}')
        return 0
    return 2


if __name__ == '__main__':
    sys.exit(main())

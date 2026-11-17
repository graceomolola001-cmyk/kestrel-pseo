"""SEO audit primitives, designed to work offline and in CI (stdlib only)."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    url: str
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


class SEOParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.in_h1 = False
        self.in_jsonld = False
        self.title: list[str] = []
        self.h1s: list[str] = []
        self.description = ''
        self.robots = ''
        self.canonical = ''
        self.links: list[str] = []
        self.jsonld_blocks: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'h1':
            self.in_h1 = True
            self.h1s.append('')
        if tag == 'meta' and data.get('name', '').lower() == 'description':
            self.description = data.get('content', '')
        if tag == 'meta' and data.get('name', '').lower() == 'robots':
            self.robots = data.get('content', '').lower()
        if tag == 'link' and 'canonical' in data.get('rel', '').lower().split():
            self.canonical = data.get('href', '')
        if tag == 'a' and data.get('href'):
            self.links.append(data['href'])
        if tag == 'script' and data.get('type', '').lower().split(';')[0].strip() == 'application/ld+json':
            self.in_jsonld = True
            self.jsonld_blocks.append('')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'script':
            self.in_jsonld = False

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.in_h1:
            self.h1s[-1] += data
        if self.in_jsonld:
            self.jsonld_blocks[-1] += data


REQUIRED = {
    'Organization': ('name', 'url'),
    'WebSite': ('name', 'url'),
    'WebPage': ('name', 'url'),
    'Article': ('headline', 'author', 'datePublished'),
    'BlogPosting': ('headline', 'author', 'datePublished'),
    'NewsArticle': ('headline', 'author', 'datePublished'),
    'Course': ('name', 'description', 'provider'),
    'FAQPage': ('mainEntity',),
    'BreadcrumbList': ('itemListElement',),
    'Product': ('name',),
    'LocalBusiness': ('name', 'address'),
}


def _schema_nodes(block, inherited_context=None):
    if isinstance(block, list):
        for item in block:
            yield from _schema_nodes(item, inherited_context)
        return
    if not isinstance(block, dict):
        return
    ctx = block.get('@context', inherited_context)
    if '@graph' in block:
        yield from _schema_nodes(block['@graph'], ctx)
    if '@type' in block:
        yield block, ctx


def validate_jsonld(blocks: list[str], url: str, require_schema: bool = False) -> list[Finding]:
    found: list[Finding] = []
    node_count = 0
    if not blocks and require_schema:
        return [Finding('error', 'SCHEMA_MISSING', url, 'No JSON-LD script found')]
    for i, block in enumerate(blocks, 1):
        try:
            payload = json.loads(block)
        except json.JSONDecodeError as exc:
            found.append(Finding('error', 'SCHEMA_JSON_INVALID', url, f'JSON-LD block {i}: {exc.msg}'))
            continue
        nodes = list(_schema_nodes(payload))
        if not nodes:
            found.append(Finding('error', 'SCHEMA_TYPE_MISSING', url, f'JSON-LD block {i} has no @type'))
        for node, context in nodes:
            node_count += 1
            if not context or (isinstance(context, str) and 'schema.org' not in context):
                found.append(Finding('error', 'SCHEMA_CONTEXT_INVALID', url, 'Missing or non-schema.org @context'))
            types = node.get('@type', [])
            types = [types] if isinstance(types, str) else types if isinstance(types, list) else []
            if not types:
                found.append(Finding('error', 'SCHEMA_TYPE_MISSING', url, 'Node lacks @type'))
            for typ in types:
                if typ not in REQUIRED:
                    continue
                for key in REQUIRED[typ]:
                    value = node.get(key)
                    if value is None or value == '' or value == []:
                        found.append(Finding('error', 'SCHEMA_REQUIRED_FIELD', url, f'{typ} missing {key}'))
                if typ == 'FAQPage' and isinstance(node.get('mainEntity'), list):
                    for item in node['mainEntity']:
                        if not isinstance(item, dict) or not item.get('name') or not isinstance(item.get('acceptedAnswer'), dict) or not item['acceptedAnswer'].get('text'):
                            found.append(Finding('error', 'SCHEMA_FAQ_QUESTION', url, 'FAQ must contain name and acceptedAnswer.text'))
                if typ == 'BreadcrumbList' and isinstance(node.get('itemListElement'), list):
                    for item in node['itemListElement']:
                        if not isinstance(item, dict) or not all(item.get(k) for k in ('position', 'name', 'item')):
                            found.append(Finding('error', 'SCHEMA_BREADCRUMB_ITEM', url, 'Breadcrumb item missing position, name or item'))
    if require_schema and node_count == 0 and not any(x.code == 'SCHEMA_MISSING' for x in found):
        found.append(Finding('error', 'SCHEMA_MISSING', url, 'No valid schema types found'))
    return found


def normalized(url: str) -> str:
    parsed = urlparse(urldefrag(url)[0]); path = parsed.path or '/'
    if path.endswith('/index.html'):
        path = path[:-10] or '/'
    return parsed._replace(path=path, fragment='', query='').geturl().rstrip('/') or url


def audit_html(html: str, url: str, expect_indexable: bool = False, require_schema: bool = False) -> tuple[list[Finding], SEOParser]:
    parser = SEOParser(); parser.feed(html)
    findings = validate_jsonld(parser.jsonld_blocks, url, require_schema)
    if not ''.join(parser.title).strip():
        findings.append(Finding('error', 'TITLE_MISSING', url, 'Title tag is empty or missing'))
    if not parser.description.strip():
        findings.append(Finding('warning', 'DESCRIPTION_MISSING', url, 'Meta description is missing'))
    if len(parser.h1s) != 1 or not parser.h1s[0].strip():
        findings.append(Finding('warning', 'H1_COUNT', url, f'Expected 1 H1, got {len(parser.h1s)}'))
    if not parser.canonical:
        findings.append(Finding('error', 'CANONICAL_MISSING', url, 'Canonical link is missing'))
    elif normalized(urljoin(url, parser.canonical)) != normalized(url):
        findings.append(Finding('warning', 'CANONICAL_MISMATCH', url, f'Canonical: {parser.canonical}'))
    if expect_indexable and 'noindex' in parser.robots:
        findings.append(Finding('error', 'UNEXPECTED_NOINDEX', url, 'Page contains noindex'))
    return findings, parser


def audit_directory(folder: str | Path, base_url: str, expect_indexable=False, require_schema=False) -> dict:
    folder = Path(folder)
    files = sorted(folder.rglob('*.html'))
    findings: list[Finding] = []
    pages: list[str] = []
    base_url = base_url.rstrip('/') + '/'
    title_map: dict[str, list[str]] = {}
    for file in files:
        rel = file.relative_to(folder).as_posix()
        url = urljoin(base_url, rel.replace('index.html', ''))
        pages.append(url)
        checked, parser = audit_html(file.read_text(encoding='utf-8'), url, expect_indexable, require_schema)
        findings.extend(checked)
        title = ''.join(parser.title).strip()
        if title:
            title_map.setdefault(title, []).append(url)
    for title, urls in title_map.items():
        if len(urls) > 1:
            findings.append(Finding('error', 'TITLE_DUPLICATE', urls[0], f'{len(urls)} pages share title {title!r}'))
    if not pages:
        findings.append(Finding('error', 'NO_HTML', base_url, 'No built HTML pages found'))
    return make_report('local', base_url, pages, findings)


def validate_redirect_map(csv_path: str | Path, known_destinations=None) -> dict:
    findings = []
    mapping = {}
    with open(csv_path, newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if not {'source', 'destination'}.issubset(set(reader.fieldnames or [])):
            raise ValueError('Redirect CSV requires source,destination columns')
        for row_num, row in enumerate(reader, start=2):
            source, dest = (row.get('source') or '').strip(), (row.get('destination') or '').strip()
            if not source and not dest:
                continue
            if not source or not dest:
                findings.append(Finding('error', 'REDIRECT_INCOMPLETE', source, f'Row {row_num} has missing source or destination'))
                continue
            if source in mapping:
                findings.append(Finding('error', 'REDIRECT_DUPLICATE', source, f'Duplicate source at row {row_num}'))
            mapping[source] = dest
            if source == dest:
                findings.append(Finding('error', 'REDIRECT_SELF', source, 'Source redirects to itself'))
            if urlparse(source).netloc and urlparse(dest).netloc and urlparse(source).netloc != urlparse(dest).netloc:
                findings.append(Finding('warning', 'REDIRECT_CROSS_DOMAIN', source, f'Destination changes host: {dest}'))
    for source in mapping:
        seen = set(); current = source
        while current in mapping:
            if current in seen:
                findings.append(Finding('error', 'REDIRECT_CYCLE', source, f'Cycle detected around {current}'))
                break
            seen.add(current); current = mapping[current]
        if len(seen) > 1 and current not in seen:
            findings.append(Finding('warning', 'REDIRECT_CHAIN', source, f'{len(seen)} redirect hops to {current}'))
        if known_destinations is not None and current not in known_destinations and not urlparse(current).netloc:
            findings.append(Finding('warning', 'REDIRECT_TARGET_UNVERIFIED', source, f'Final destination {current} absent from known paths'))
    return make_report('redirects', str(csv_path), list(mapping), findings)


def make_report(mode: str, target: str, pages: list[str], findings: list[Finding]) -> dict:
    from datetime import datetime, timezone
    return {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(), 'mode': mode,
            'target': target, 'pages_checked': len(pages), 'pages': pages,
            'counts': {sev: sum(f.severity == sev for f in findings) for sev in ('error', 'warning', 'info')},
            'findings': [f.to_dict() for f in findings],
            'status': 'fail' if any(f.severity == 'error' for f in findings) else 'pass'}

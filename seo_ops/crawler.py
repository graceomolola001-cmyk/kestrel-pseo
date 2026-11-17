"""Bounded same-site crawler with robots.txt compliance and polite pacing."""
from __future__ import annotations

import time
from collections import deque
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urldefrag, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

from .core import Finding, audit_html, make_report, normalized

AGENT = 'GraceSEOOperationsAudit/1.0 (respectful portfolio audit)'


def crawl(start_url: str, max_pages=30, delay=0.3, expect_indexable=False, require_schema=False, fetch=None):
    parsed_start = urlparse(start_url)
    if parsed_start.scheme not in ('http', 'https') or not parsed_start.netloc:
        raise ValueError('Provide an absolute http(s) URL')
    origin = f'{parsed_start.scheme}://{parsed_start.netloc}'
    root = parsed_start.path.rstrip('/') + '/'
    robots = RobotFileParser()
    robots.set_url(origin + '/robots.txt')
    try:
        robots.read()
    except (HTTPError, URLError, OSError):
        pass
    queue = deque([start_url]); visited = set(); findings = []; pages = []
    fetch = fetch or _fetch
    while queue and len(visited) < max_pages:
        url = urldefrag(queue.popleft())[0]
        p = urlparse(url)
        if p.netloc != parsed_start.netloc or not p.path.startswith(root):
            continue
        key = normalized(url)
        if key in visited:
            continue
        visited.add(key)
        if not robots.can_fetch(AGENT, url):
            findings.append(Finding('info', 'ROBOTS_DISALLOW', url, 'robots.txt blocks this URL; skipped'))
            continue
        try:
            status, final_url, body = fetch(url)
            if urlparse(final_url).netloc != parsed_start.netloc:
                findings.append(Finding('warning', 'OFFSITE_REDIRECT', url, final_url))
                continue
            if status >= 400:
                findings.append(Finding('error', 'HTTP_ERROR', url, f'Status {status}'))
                continue
            if normalized(final_url) != normalized(url):
                findings.append(Finding('info', 'REDIRECT', url, f'Moved to {final_url}'))
            pages.append(final_url)
            page_findings, parser = audit_html(body, final_url, expect_indexable, require_schema)
            findings.extend(page_findings)
            for raw in parser.links:
                target = urldefrag(urljoin(final_url, raw))[0]
                target_p = urlparse(target)
                if (target_p.scheme in ('http', 'https') and target_p.netloc == parsed_start.netloc
                        and target_p.path.startswith(root) and normalized(target) not in visited):
                    queue.append(target)
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeError) as exc:
            findings.append(Finding('error', 'REQUEST_FAILED', url, str(exc)))
        if delay:
            time.sleep(delay)
    if not pages:
        findings.append(Finding('error', 'NO_PAGES_CRAWLED', start_url, 'No live HTML pages audited; check deployment, robots rules and start path'))
    return make_report('live', start_url, pages, findings)


def _fetch(url):
    request = Request(url, headers={'User-Agent': AGENT, 'Accept': 'text/html'})
    with urlopen(request, timeout=12) as response:
        final = response.geturl(); status = response.status
        body = response.read(2_000_000).decode('utf-8', errors='replace')
    return status, final, body

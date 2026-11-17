import tempfile
import unittest
from pathlib import Path
from seo_ops.core import audit_directory, audit_html, validate_jsonld, validate_redirect_map
from seo_ops.crawler import crawl


GOOD = '''<html><head><title>Demo page</title><meta name="description" content="Unique demo content page for QA">
<link rel="canonical" href="https://example.com/demo/"><script type="application/ld+json">
{"@context":"https://schema.org","@type":"Article","headline":"Demo","author":{"@type":"Person","name":"Grace"},"datePublished":"2026-11-17"}
</script></head><body><h1>Demo</h1></body></html>'''


class TestSchema(unittest.TestCase):
    def test_valid_article(self):
        findings, _ = audit_html(GOOD, 'https://example.com/demo/', require_schema=True)
        self.assertEqual([f for f in findings if f.severity == 'error'], [])

    def test_invalid_json(self):
        failures = validate_jsonld(['{"@context":'], 'https://example.com', True)
        self.assertIn('SCHEMA_JSON_INVALID', [f.code for f in failures])

    def test_missing_required_type_field(self):
        findings = validate_jsonld(['{"@context":"https://schema.org","@type":"Article","headline":"A"}'], 'https://example.com')
        self.assertEqual(sum(f.code=='SCHEMA_REQUIRED_FIELD' for f in findings), 2)

    def test_schema_graph_inherited_context(self):
        jsonld = '{"@context":"https://schema.org","@graph":[{"@type":"Organization","name":"A","url":"https://example.com"}]}'
        self.assertFalse(validate_jsonld([jsonld], 'https://example.com', True))

    def test_noindex_flag(self):
        html = GOOD.replace('<h1>', '<meta name="robots" content="noindex"><h1>')
        findings, _ = audit_html(html, 'https://example.com/demo/', expect_indexable=True)
        self.assertIn('UNEXPECTED_NOINDEX', [f.code for f in findings])

    def test_local_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'demo'; path.mkdir()
            (path/'index.html').write_text(GOOD, encoding='utf-8')
            report = audit_directory(tmp, 'https://example.com/')
            self.assertEqual(report['pages_checked'], 1)
            self.assertEqual(report['status'], 'pass')

    def test_redirect_chain_and_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp)/'r.csv'
            file.write_text('source,destination\n/a,/b\n/b,/c\n/x,/y\n/y,/x\n',encoding='utf-8')
            report = validate_redirect_map(file)
            codes = [f['code'] for f in report['findings']]
            self.assertIn('REDIRECT_CHAIN', codes)
            self.assertIn('REDIRECT_CYCLE', codes)
            self.assertEqual(report['status'], 'fail')

    def test_bounded_live_crawl(self):
        # Fake responses permit deterministic tests without external network calls.
        from unittest.mock import patch
        with patch('seo_ops.crawler.RobotFileParser') as fake_robots:
            fake_robots.return_value.can_fetch.return_value = True
            result = crawl('https://example.com/demo/', max_pages=1, delay=0,
                           fetch=lambda url: (200, url, GOOD))
        self.assertEqual(result['pages_checked'], 1)
        self.assertEqual(result['status'], 'pass')

    def test_no_redirects_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp)/'r.csv'
            file.write_text('source,destination\n', encoding='utf-8')
            self.assertEqual(validate_redirect_map(file)['status'], 'pass')


if __name__=='__main__':unittest.main()

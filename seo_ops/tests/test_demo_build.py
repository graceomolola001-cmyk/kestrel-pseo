"""Regression tests for the public fictional demo build."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://graceomolola001-cmyk.github.io/kestrel-pseo"

class DemoBuildTests(unittest.TestCase):
    def test_fictional_site_is_crawlable_but_noindex(self):
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run(
                [sys.executable, str(ROOT / "build.py"),
                 "--out", folder, "--base-url", BASE],
                cwd=ROOT, capture_output=True, text=True, check=False
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            home = (Path(folder) / "index.html").read_text(encoding="utf-8")
            robots = (Path(folder) / "robots.txt").read_text(encoding="utf-8")
            self.assertIn('content="noindex, nofollow"', home)
            self.assertIn('data-programme-search', home)
            self.assertIn('data-programme-card', home)
            self.assertIn('href="/kestrel-pseo/programmes/"', home)
            self.assertIn("Allow: /", robots)
            self.assertNotIn("Disallow: /", robots)
            self.assertFalse((Path(folder) / "sitemap.xml").exists())

if __name__ == "__main__":
    unittest.main()

"""Regression tests for the public fictional demo build."""
from pathlib import Path
import os
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
            self.assertIn('href="/kestrel-pseo/programmes/"', home)
            self.assertIn("Allow: /", robots)
            self.assertIn('href="/kestrel-pseo/assets/site.css"', home)
            self.assertIn('src="/kestrel-pseo/assets/site.js"', home)
            self.assertIn('data-audit-feed="/kestrel-pseo/seo-health.json"', home)
            for section in ("systems", "lab", "reports", "programmes"):
                self.assertTrue((Path(folder) / section / "index.html").exists(), section)
            lab = (Path(folder) / "lab" / "index.html").read_text(encoding="utf-8")
            catalogue = (Path(folder) / "programmes" / "index.html").read_text(encoding="utf-8")
            reports = (Path(folder) / "reports" / "index.html").read_text(encoding="utf-8")
            systems = (Path(folder) / "systems" / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-scenario="noindex"', lab)
            self.assertIn('SIMULATION ONLY', lab)
            self.assertIn('data-market-filter="all"', catalogue)
            self.assertIn('data-programme-search', catalogue)
            self.assertIn('data-programme-card', catalogue)
            self.assertIn("See the sample course pages", catalogue)
            self.assertIn("The school and courses are made up.", home)
            self.assertIn('data-audit-feed="/kestrel-pseo/seo-health.json"', reports)
            self.assertIn("From a table", systems)
            self.assertIn('href="/kestrel-pseo/lab/"', home)
            self.assertIn('href="/kestrel-pseo/systems/"', home)
            self.assertIn('href="/kestrel-pseo/reports/"', home)
            self.assertIn("Find SEO problems", home)
            self.assertIn('class="editorial-photo-story"', home)
            self.assertIn('class="catalogue-cover-photo"', catalogue)
            self.assertIn('class="systems-photo"', systems)
            for document in (home, catalogue, systems):
                self.assertIn('loading="lazy"', document)
                self.assertIn('decoding="async"', document)
                self.assertIn(' alt="', document)
                self.assertIn('images.unsplash.com/', document)
            self.assertTrue((Path(folder) / "assets" / "site.css").is_file())
            self.assertTrue((Path(folder) / "assets" / "site.js").is_file())
            self.assertIn('prefers-reduced-motion', (Path(folder) / "assets" / "site.css").read_text(encoding="utf-8"))
            self.assertIn('fetch(url,', (Path(folder) / "assets" / "site.js").read_text(encoding="utf-8"))
            self.assertNotIn("Disallow: /", robots)
            self.assertFalse((Path(folder) / "sitemap.xml").exists())


    def test_optional_google_tag_and_gsc_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            env = os.environ.copy()
            env["KESTREL_GA4_MEASUREMENT_ID"] = "G-TEST123456"
            env["KESTREL_GSC_VERIFICATION_TOKEN"] = "testverification123_xyz"
            run = subprocess.run(
                [sys.executable, str(ROOT / "build.py"),
                 "--out", folder, "--base-url", BASE],
                cwd=ROOT, env=env, capture_output=True, text=True, check=False
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            home = (Path(folder) / "index.html").read_text(encoding="utf-8")
            self.assertIn('name="google-site-verification"', home)
            self.assertIn('content="testverification123_xyz"', home)
            self.assertIn('googletagmanager.com/gtag/js?id=G-TEST123456', home)
            self.assertIn("gtag('config', \"G-TEST123456\")", home)
            self.assertIn('content="noindex, nofollow"', home)

    def test_invalid_measurement_id_blocks_build(self):
        with tempfile.TemporaryDirectory() as folder:
            env = os.environ.copy()
            env["KESTREL_GA4_MEASUREMENT_ID"] = "<script>alert(1)</script>"
            env.pop("KESTREL_GSC_VERIFICATION_TOKEN", None)
            run = subprocess.run(
                [sys.executable, str(ROOT / "build.py"),
                 "--out", folder, "--base-url", BASE],
                cwd=ROOT, env=env, capture_output=True, text=True, check=False
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse((Path(folder) / "index.html").exists())

if __name__ == "__main__":
    unittest.main()

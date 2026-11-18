"""Checks Kestrel's synthetic 500-page scale harness without public deployment."""
import json
from pathlib import Path
import tempfile
import unittest

from seo_ops.scale_test import fixture_rows, run


class ScaleTestHarnessTests(unittest.TestCase):
    def test_fixtures_have_unique_page_keys(self):
        records = fixture_rows(500)
        self.assertEqual(len(records), 500)
        self.assertEqual(len({(r["programme"], r["country"]) for r in records}), 500)
        self.assertTrue(all(r["source"].startswith("GENERATED TEST FIXTURE") for r in records))
        self.assertTrue(all(r["status"] == "publish" for r in records))

    def test_small_scale_uses_real_build_and_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fixture-run"
            result = run(count=8, output=str(out))
            self.assertEqual(result["generated_programme_pages"], 8)
            self.assertEqual(result["html_pages_checked"], 13)
            self.assertEqual(result["seo_errors"], 0)
            self.assertFalse(result["publicly_deployed"])
            self.assertEqual(result["unique_canonicals"], 13)
            self.assertIn("UNEXPECTED_NOINDEX", result["fault_injection"]["detected_issue_codes"])
            saved = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["qa_exit_status"], "PASS")


if __name__ == "__main__":
    unittest.main()

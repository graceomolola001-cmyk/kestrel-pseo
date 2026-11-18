"""Smoke-test the API verification logic without making external requests."""
import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from seo_ops.google_probe import SITE, _check_ga4, _check_gsc


class GoogleProbeTests(unittest.TestCase):
    @patch("seo_ops.google_data.query_ga4")
    def test_ga4_api_rows(self, query):
        query.return_value = [{"date": "20261118", "sessions": "3", "key_events": "0"}]
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(_check_ga4("565038230"), 0)
        self.assertIn("3 reported sessions", buffer.getvalue())

    @patch("seo_ops.google_data.query_gsc")
    @patch("seo_ops.google_data._session")
    def test_gsc_empty_query_is_valid(self, factory, query):
        response = Mock()
        response.json.return_value = {"siteEntry": [{"siteUrl": SITE}]}
        factory.return_value.get.return_value = response
        query.return_value = []
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(_check_gsc(SITE), 0)
        self.assertIn("0 page rows", buffer.getvalue())

    @patch("seo_ops.google_data.query_gsc")
    @patch("seo_ops.google_data._session")
    def test_missing_gsc_permission_is_reported(self, factory, query):
        response = Mock()
        response.json.return_value = {"siteEntry": []}
        factory.return_value.get.return_value = response
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(_check_gsc(SITE), 2)
        query.assert_not_called()
        self.assertIn("accessible: NO", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()

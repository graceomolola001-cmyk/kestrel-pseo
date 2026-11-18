"""Validate importable local n8n Google API demo without credentials or network."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / "integrations" / "n8n" / "kestrel-google-apis-demo.json"

class GoogleN8nWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = WORKFLOW.read_text(encoding="utf-8")
        cls.workflow = json.loads(cls.raw)

    def test_no_credentials_in_export(self):
        low = self.raw.lower()
        self.assertNotIn("private_key", low)
        self.assertNotIn("client_secret", low)
        self.assertNotIn('"credentials": {', low)
        self.assertEqual(self.workflow["active"], False)

    def test_expected_nodes_and_connections(self):
        nodes = {node["name"]: node for node in self.workflow["nodes"]}
        expected = [
            "Run API demo", "GA4 Data API", "GA4 Realtime API",
            "Search Console API", "Published SEO audit", "Build verified SEO report",
            "Any technical errors?", "Review technical findings", "No critical issues in scope"
        ]
        self.assertEqual(set(nodes), set(expected))
        self.assertEqual(len(set(node["id"] for node in nodes.values())), len(nodes))
        for name in ("GA4 Data API", "GA4 Realtime API", "Search Console API"):
            params = nodes[name]["parameters"]
            self.assertEqual(params["authentication"], "predefinedCredentialType")
            self.assertEqual(params["nodeCredentialType"], "googleApi")
            self.assertEqual(params["method"], "POST")
        self.assertEqual(nodes["Published SEO audit"]["parameters"]["method"], "GET")
        self.assertIn("565038230", self.raw)
        self.assertIn("seo-health.json", self.raw)
        self.assertIn("runRealtimeReport", self.raw)

    def test_empty_data_is_handled_explicitly(self):
        node = next(n for n in self.workflow["nodes"] if n["name"] == "Build verified SEO report")
        code = node["parameters"]["jsCode"]
        self.assertIn("Array.isArray(ga4.rows)", code)
        self.assertIn("Array.isArray(gsc.rows)", code)
        self.assertIn("No search rows yet", code)
        self.assertIn("No standard report rows yet", code)
        self.assertIn("no search or session metrics are invented", code.lower())

    def test_connected_graph_reaches_both_outputs(self):
        connections = self.workflow["connections"]
        pointer = "Run API demo"
        visited = set()
        while pointer != "Any technical errors?":
            self.assertNotIn(pointer, visited, "Cycle before decision")
            visited.add(pointer)
            pointer = connections[pointer]["main"][0][0]["node"]
        terminal = connections[pointer]["main"]
        self.assertEqual({branch[0]["node"] for branch in terminal},
            {"Review technical findings", "No critical issues in scope"})

if __name__ == "__main__":
    unittest.main()

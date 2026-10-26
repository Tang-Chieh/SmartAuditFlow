import json
import unittest

from src.workflow.nodes import (
    AuditPlanNode,
    FormatConverterNode,
    InitialAnalysisNode,
    IterationNode,
)


class FakeModelManager:
    def __init__(self, response):
        self.response = response
        self.prompts = []

    def call_model_sync(self, prompt):
        self.prompts.append(prompt)
        return self.response


class PriceFocusedPromptTests(unittest.TestCase):
    def test_analysis_plan_iteration_and_finalize_are_price_scoped(self):
        cases = [
            (InitialAnalysisNode, {}, "initial analysis"),
            (AuditPlanNode, {"1728096797608": {"analysis": "oracle flow"}}, "1. Trace oracle to redemption"),
            (
                IterationNode,
                {"1728114018925": {"tasks": [{"id": 1, "task": "Trace spot price into liquidation", "priority": "high"}]}},
                "Finding: none",
            ),
            (
                FormatConverterNode,
                {"1728114855021": {"task_results": []}},
                "[]",
            ),
        ]
        for node_type, context, response in cases:
            manager = FakeModelManager(response)
            node = node_type("test", "llm", manager)
            node.execute_sync({"code_snippet": "contract Pool {}", **context})
            self.assertIn("price-manipulation", manager.prompts[0].lower())
            self.assertIn("attacker-influenceable", manager.prompts[0].lower())


class PredictionShapeTests(unittest.TestCase):
    def setUp(self):
        self.finding = {
            "finding_id": "SAF-001",
            "title": "AMM spot price can be manipulated during redemption",
            "description": "The redemption path uses the current pool spot price without a manipulation-resistant check.",
            "impact": "An attacker can temporarily distort the redemption value and extract excess assets.",
            "vulnerable_code": [{
                "file": "src/Pool.sol",
                "contract": "Pool",
                "function": "redeem",
                "start_line": 42,
                "end_line": 48,
            }],
            "mitigation": "Use a sufficiently long TWAP or an independent oracle with freshness and deviation bounds.",
            "severity": "High",
        }

    def _run_finalize(self, response):
        manager = FakeModelManager(response)
        node = FormatConverterNode("test", "llm", manager)
        source_body = "\n".join("contract Pool {}" for _ in range(60))
        result = node.execute_sync({
            "code_snippet": (
                "// ===== BEGIN SOURCE FILE: src/Pool.sol =====\n"
                + source_body
                + "\n// ===== END SOURCE FILE: src/Pool.sol ====="
            ),
            "static_tool": "",
            "model_choice": "test-model",
            "1728114855021": {"task_results": []},
        })
        return result, manager.prompts[0]

    def test_emits_prediction_fields_and_keeps_legacy_findings(self):
        result, prompt = self._run_finalize(json.dumps([self.finding]))
        self.assertEqual(result["Predictions"], [self.finding])
        self.assertEqual(result["FindingNumber"], 1)
        self.assertEqual(result["Findings"][0]["Issue"], self.finding["title"])
        self.assertEqual(result["Findings"][0]["Mitigation"], self.finding["mitigation"])
        self.assertIn('"vulnerable_code"', prompt)
        self.assertIn('"mitigation"', prompt)
        self.assertIn("static analysis results (may be empty)", prompt.lower())

    def test_empty_array_is_valid_and_does_not_create_synthetic_findings(self):
        result, _ = self._run_finalize("[]")
        self.assertEqual(result["Predictions"], [])
        self.assertEqual(result["Findings"], [])
        self.assertEqual(result["OutputWarnings"], [])

    def test_missing_mitigation_is_rejected_not_filled_with_a_placeholder(self):
        incomplete = {key: value for key, value in self.finding.items() if key != "mitigation"}
        result, _ = self._run_finalize(json.dumps([incomplete]))
        self.assertEqual(result["Predictions"], [])
        self.assertEqual(len(result["OutputWarnings"]), 1)
        self.assertIn("mitigation", result["OutputWarnings"][0])

    def test_invalid_vulnerable_code_location_is_rejected_and_warned(self):
        invalid_refs = [
            {
                **self.finding,
                "vulnerable_code": [{
                    **self.finding["vulnerable_code"][0],
                    "file": "src/Missing.sol",
                }],
            },
            {
                **self.finding,
                "vulnerable_code": [{
                    **self.finding["vulnerable_code"][0],
                    "start_line": 61,
                    "end_line": 62,
                }],
            },
        ]

        for finding in invalid_refs:
            with self.subTest(vulnerable_code=finding["vulnerable_code"]):
                result, _ = self._run_finalize(json.dumps([finding]))
                self.assertEqual(result["Predictions"], [])
                self.assertEqual(len(result["OutputWarnings"]), 1)
                self.assertIn(
                    "invalid vulnerable_code location", result["OutputWarnings"][0]
                )

    def test_unparseable_json_does_not_become_a_fake_finding(self):
        result, _ = self._run_finalize("No valid JSON output")
        self.assertEqual(result["Predictions"], [])
        self.assertEqual(result["Findings"], [])
        self.assertTrue(result["OutputWarnings"])


if __name__ == "__main__":
    unittest.main()

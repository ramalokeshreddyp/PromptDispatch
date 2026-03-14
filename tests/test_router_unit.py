"""
Unit tests for router core behavior.

Run:
    python -m unittest tests/test_router_unit.py -v
"""

import json
import os
import tempfile
import unittest

from app import router


class RouterUnitTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Isolate log output for each test.
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.old_log_file = os.environ.get("LOG_FILE")
        self.log_file = os.path.join(self.tmp_dir.name, "route_log.jsonl")
        os.environ["LOG_FILE"] = self.log_file

        # Keep module logger in sync with env override.
        from app import logger as logger_module

        logger_module.LOG_FILE = self.log_file

    async def asyncTearDown(self):
        if self.old_log_file is None:
            os.environ.pop("LOG_FILE", None)
        else:
            os.environ["LOG_FILE"] = self.old_log_file
        self.tmp_dir.cleanup()

    def _read_log_entries(self):
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def test_parse_classification_valid_json(self):
        out = router._parse_classification('{"intent":"code","confidence":0.93}')
        self.assertEqual(out["intent"], "code")
        self.assertEqual(out["confidence"], 0.93)

    def test_parse_classification_invalid_json_defaults_to_unclear(self):
        out = router._parse_classification("intent=code confidence=0.93")
        self.assertEqual(out, {"intent": "unclear", "confidence": 0.0})

    async def test_route_and_respond_unclear_returns_question_and_logs(self):
        result = await router.route_and_respond(
            "help me",
            {"intent": "unclear", "confidence": 0.2},
        )

        self.assertTrue(result.endswith("?"))
        self.assertIn("coding", result.lower())

        entries = self._read_log_entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]

        self.assertIn("intent", entry)
        self.assertIn("confidence", entry)
        self.assertIn("user_message", entry)
        self.assertIn("final_response", entry)

        self.assertEqual(entry["intent"], "unclear")
        self.assertEqual(entry["user_message"], "help me")
        self.assertEqual(entry["final_response"], result)


if __name__ == "__main__":
    unittest.main()


import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from summary_func import (
    build_summary,
    print_summary,
    write_summary_report,
)


class TestBackupSummary(unittest.TestCase):

    def test_all_success_status(self):
        summary = build_summary(3, 3, 0, [])
        self.assertEqual(summary["status"], "success")

    def test_partial_failure_status(self):
        failures = [{"device": "SW2", "error": "Connection timeout"}]
        summary = build_summary(3, 2, 1, failures)

        self.assertEqual(summary["status"], "partial")
        self.assertEqual(summary["failed_devices"], failures)

    def test_all_failed_status(self):
        summary = build_summary(
            2,
            0,
            2,
            [
                {"device": "SW1", "error": "Timeout"},
                {"device": "SW2", "error": "Authentication failed"},
            ],
        )
        self.assertEqual(summary["status"], "failed")

    def test_write_and_read_json_report(self):
        summary = build_summary(2, 1, 1, [
            {"device": "SW2", "error": "Connection timeout"}
        ])

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "reports" / "summary.json"
            result_path = write_summary_report(summary, report_path)

            self.assertTrue(result_path.exists())

            with result_path.open(encoding="utf-8") as report_file:
                loaded = json.load(report_file)

        self.assertEqual(loaded["status"], "partial")
        self.assertEqual(loaded["total_devices"], 2)
        self.assertEqual(loaded["failed_devices"][0]["device"], "SW2")
        datetime.fromisoformat(loaded["timestamp"])

    @patch("summary_func.write_summary_report")
    @patch("builtins.print")
    def test_print_summary_calls_report_writer(
        self,
        mock_print,
        mock_write_report,
    ):
        result = print_summary(
            total_devices=2,
            success_count=1,
            failed_count=1,
            failed_devices=[
                {"device": "SW2", "error": "Timeout"}
            ],
            report_path="test_summary.json",
        )

        self.assertEqual(result["status"], "partial")
        mock_write_report.assert_called_once_with(
            result,
            "test_summary.json",
        )


if __name__ == "__main__":
    unittest.main()

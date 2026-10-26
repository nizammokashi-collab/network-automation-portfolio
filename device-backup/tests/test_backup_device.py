
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backup_device_func import backup_device


class TestBackupDevice(unittest.TestCase):

    @patch("backup_device_func.ConnectHandler")
    def test_backup_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.send_command.return_value = "Cisco IOS test output"

        with tempfile.TemporaryDirectory() as temp_dir:
            backup_folder = Path(temp_dir)

            success, error = backup_device(
                "SW1",
                {
                    "device_type": "cisco_ios",
                    "host": "192.0.2.10",
                    "username": "test_user",
                    "password": "test_password",
                },
                backup_folder,
                ["show version"],
            )

            saved_file = backup_folder / "SW1" / "SHOW_VERSION.txt"

            self.assertTrue(success)
            self.assertIsNone(error)
            self.assertTrue(saved_file.exists())
            self.assertEqual(
                saved_file.read_text(encoding="utf-8"),
                "Cisco IOS test output",
            )

        mock_connection.disconnect.assert_called_once()

    @patch("backup_device_func.ConnectHandler")
    def test_backup_connection_failure(self, mock_connect):
        mock_connect.side_effect = ConnectionError(
            "Simulated connection failure"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertLogs(
                "backup_device_func", level="ERROR"
            ) as captured_logs:
                success, error = backup_device(
                    "SW1",
                    {
                        "device_type": "cisco_ios",
                        "host": "192.0.2.10",
                        "username": "test_user",
                        "password": "test_password",
                    },
                    Path(temp_dir),
                    ["show version"],
                )

        self.assertFalse(success)
        self.assertEqual(error, "Simulated connection failure")
        self.assertTrue(
            any("Backup failed for SW1" in message
                for message in captured_logs.output)
        )

    @patch("backup_device_func.ConnectHandler")
    def test_backup_command_failure(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        mock_connection.send_command.side_effect = RuntimeError(
            "Simulated command failure"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertLogs(
                "backup_device_func", level="ERROR"
            ) as captured_logs:
                success, error = backup_device(
                    "SW1",
                    {
                        "device_type": "cisco_ios",
                        "host": "192.0.2.10",
                        "username": "test_user",
                        "password": "test_password",
                    },
                    Path(temp_dir),
                    ["show version"],
                )

        self.assertFalse(success)
        self.assertEqual(error, "Simulated command failure")
        self.assertTrue(
            any("Backup failed for SW1" in message
                for message in captured_logs.output)
        )
        mock_connection.disconnect.assert_called_once()


if __name__ == "__main__":
    unittest.main()

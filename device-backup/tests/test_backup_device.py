
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backup_device_func import backup_device


class TestBackupDevice(unittest.TestCase):

    def setUp(self):
        self.device = {
            "device_type": "cisco_ios",
            "host": "192.0.2.10",
            "username": "test_user",
            "password": "test_password",
        }

    @patch("backup_device_func.ConnectHandler")
    def test_backup_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.send_command.return_value = "Cisco IOS test output"

        with tempfile.TemporaryDirectory() as temp_dir:
            success, error = backup_device(
                "SW1",
                self.device,
                Path(temp_dir),
                ["show version"],
            )

            saved_file = (
                Path(temp_dir) / "SW1" / "SHOW_VERSION.txt"
            )

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
            ):
                success, error = backup_device(
                    "SW1",
                    self.device,
                    Path(temp_dir),
                    ["show version"],
                )

        self.assertFalse(success)
        self.assertEqual(error, "Simulated connection failure")
        mock_connect.assert_called_once()

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
            ):
                success, error = backup_device(
                    "SW1",
                    self.device,
                    Path(temp_dir),
                    ["show version"],
                )

        self.assertFalse(success)
        self.assertIn("show version", error)
        mock_connection.disconnect.assert_called_once()

    @patch("backup_device_func.ConnectHandler")
    def test_partial_backup_failure(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        def simulated_command(command):
            if command == "show running-config":
                raise RuntimeError("Simulated command failure")
            return "Version output"

        mock_connection.send_command.side_effect = simulated_command

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertLogs(
                "backup_device_func", level="ERROR"
            ):
                success, error = backup_device(
                    "SW1",
                    self.device,
                    Path(temp_dir),
                    ["show version", "show running-config"],
                )

            version_file = (
                Path(temp_dir) / "SW1" / "SHOW_VERSION.txt"
            )

            self.assertTrue(version_file.exists())
            self.assertEqual(
                version_file.read_text(encoding="utf-8"),
                "Version output",
            )

        self.assertFalse(success)
        self.assertIn("show running-config", error)
        mock_connection.disconnect.assert_called_once()
        self.assertEqual(mock_connection.send_command.call_count, 2)

    @patch("backup_device_func.ConnectHandler")
    def test_invalid_inventory_does_not_connect(self, mock_connect):
        invalid_device = {
            "device_type": "cisco_ios",
            "host": "192.0.2.10",
            "username": "test_user",
            "password": "",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            success, error = backup_device(
                "SW1",
                invalid_device,
                Path(temp_dir),
                ["show version"],
            )

        self.assertFalse(success)
        self.assertIn("password", error)
        mock_connect.assert_not_called()

    @patch("backup_device_func.ConnectHandler")
    def test_empty_command_list_does_not_connect(self, mock_connect):
        with tempfile.TemporaryDirectory() as temp_dir:
            success, error = backup_device(
                "SW1",
                self.device,
                Path(temp_dir),
                [],
            )

        self.assertFalse(success)
        self.assertIn("No backup commands", error)
        mock_connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()

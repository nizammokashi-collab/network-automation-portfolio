# Device Backup Automation - Unit Tests

## Purpose

These unit tests validate the device backup function without connecting to real network devices.

## Test Cases

1. **Backup success** - verifies command output is saved to a file.
2. **Connection failure** - verifies connection errors are handled.
3. **Command failure** - verifies command errors are handled and the connection is disconnected.

## Technologies

- Python unittest
- unittest.mock
- tempfile
- Netmiko (mocked during testing)

## Run Tests

From the repository root:

```bash
python -m unittest discover -s device-backup/tests -v
```

All tests use mocked connections and do not require device credentials or network access.
# Device Backup Automation - Unit Tests

## Purpose

These unit tests validate device backup behavior and JSON summary reporting without connecting to real network devices.

## Test Cases

### Device Backup Tests

1. **Backup success** - verifies command output is saved.
2. **Connection failure** - verifies connection errors are handled.
3. **Command failure** - verifies command errors are handled and the connection is disconnected.
4. **Empty command list** - verifies invalid backup configuration is rejected before connecting.
5. **Invalid inventory** - verifies required device fields are checked before connecting.
6. **Partial backup failure** - verifies a backup can report failed commands while handling the result appropriately.

### Summary Reporting Tests

7. **All-success status** - verifies the summary status when all devices succeed.
8. **Partial-failure status** - verifies the summary status when some devices fail.
9. **All-failed status** - verifies the summary status when all devices fail.
10. **JSON report** - verifies the report can be written and read with expected fields.
11. **Report writer integration** - verifies the summary function calls the report writer.

## Technologies

- Python `unittest`
- `unittest.mock`
- `tempfile`
- Netmiko (mocked during tests)
- JSON

## Run Tests

From the repository root:

```bash
python -m unittest discover -s device-backup/tests -v
```

All tests use mocked device connections and do not require device credentials or network access.
# Network Automation Portfolio

Python-based network automation projects built through hands-on labs. This repository demonstrates device backup workflows, error handling, automated testing, simulated API data processing, and reporting.

## Projects

### 1. Device Backup Automation

A modular Python project that:

- Loads device inventory and backup commands.
- Connects to network devices using Netmiko.
- Saves command output in backup files.
- Handles connection, configuration, and command failures.
- Logs execution details.
- Tracks successful and failed backups.
- Generates a console summary and JSON summary report.

**Testing:** Unit tests use mocked device connections, so they can validate backup behavior without connecting to real network devices.

### 2. Device Health and Inventory API

A Python project using simulated API responses to demonstrate:

- Cursor-based pagination.
- Retry handling for temporary API errors and rate limiting.
- Device record validation and normalization.
- Duplicate detection and conflict identification.
- Filtering, sorting, and aggregation.
- JSON reporting.

**Note:** This project uses simulated API data and does not connect to a live network API.

## Technologies

- Python
- Netmiko
- REST API concepts and HTTP response handling
- JSON and YAML
- Exception handling and logging
- Unit testing with `unittest` and `unittest.mock`
- Git, GitHub, and GitHub Actions

## Run the Tests

From the repository root:

```bash
python -m unittest discover -s device-backup/tests -v
```

The backup unit tests use mocked connections and do not require live device access.

## Repository Structure

```text
.github/workflows/       GitHub Actions test workflow
device-backup/           Device backup automation
device-health-inventory/ Simulated API inventory processing
requirements.txt         Python dependencies
```

## Security

- Use sanitized sample data in public examples.
- Do not commit credentials, API tokens, private keys, or confidential company configurations.
- The local device inventory is excluded from version control; `devices.yaml.example` provides a sample structure.

## Project Status

The repository contains completed hands-on exercises and automated tests for the projects described above. The projects are learning and portfolio demonstrations, not claims of production deployment.

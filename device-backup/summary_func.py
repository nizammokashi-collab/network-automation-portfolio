
import json
from datetime import datetime, timezone
from pathlib import Path


def build_summary(total_devices, success_count, failed_count, failed_devices):
    """Build a machine-readable summary of a backup run."""
    if failed_count == 0:
        status = "success"
    elif success_count == 0:
        status = "failed"
    else:
        status = "partial"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "total_devices": total_devices,
        "successful": success_count,
        "failed": failed_count,
        "failed_devices": failed_devices,
    }


def write_summary_report(summary, report_path):
    """Write the summary to a JSON file."""
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(summary, report_file, indent=4)

    return report_path


def print_summary(
    total_devices,
    success_count,
    failed_count,
    failed_devices,
    report_path="backup_summary.json",
):
    """Print the console summary and save a JSON report."""
    summary = build_summary(
        total_devices,
        success_count,
        failed_count,
        failed_devices,
    )

    print("\n" + "=" * 60)
    print("NETWORK BACKUP SUMMARY")
    print("=" * 60)
    print(f"Total Devices : {total_devices}")
    print(f"Successful    : {success_count}")
    print(f"Failed        : {failed_count}")
    print(f"Status        : {summary['status'].upper()}")

    if failed_devices:
        print("\nFailed Devices")
        print("-" * 60)

        for device in failed_devices:
            print(f"{device['device']}")
            print(f"Error : {device['error']}")
            print("-" * 60)

    write_summary_report(summary, report_path)
    print(f"JSON Report   : {report_path}")
    print("Backup Process Finished")
    print("=" * 60)

    return summary

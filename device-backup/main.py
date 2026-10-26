
import logging

from backup_folder_func import create_backup_folder
from inventory_func import load_inventory
from command_func import get_commands
from backup_device_func import backup_device
from summary_func import print_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("device_backup.log", encoding="utf-8"),
    ],
)

# Read inventory and backup configuration.
devices = load_inventory()
backup_folder = create_backup_folder()
commands = get_commands()

# Track backup results.
total_devices = len(devices)
success_count = 0
failed_count = 0
failed_devices = []

# Back up each device.
for device_name, device in devices.items():
    success, error = backup_device(
        device_name,
        device,
        backup_folder,
        commands,
    )

    if success:
        success_count += 1
    else:
        failed_count += 1
        failed_devices.append({
            "device": device_name,
            "error": error,
        })

# Print and save the summary.
print_summary(
    total_devices=total_devices,
    success_count=success_count,
    failed_count=failed_count,
    failed_devices=failed_devices,
    report_path=backup_folder / "backup_summary.json",
)

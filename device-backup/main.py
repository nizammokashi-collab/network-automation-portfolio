
from backup_folder_func import create_backup_folder
from inventory_func import load_inventory
from command_func import get_commands
from backup_device_func import backup_device
from summary_func import print_summary

# Read inventory file
devices = load_inventory()

# Create dynamic backup folder
backup_folder = create_backup_folder()

#Get commands
commands = get_commands()

# Backup counters
total_devices = len(devices)
success_count = 0
failed_count = 0
failed_devices = []
#............

#Backup devices
for device_name, device in devices.items():
    success, error = backup_device(device_name, device, backup_folder, commands)

    if success:
        success_count += 1
    else:
        failed_count += 1

        failed_devices.append(
            {
                "device": device_name,
                "error": error,
            }
        )

# Display summary
print_summary(total_devices = total_devices, success_count = success_count, failed_count = failed_count, failed_devices = failed_devices)

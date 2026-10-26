
from netmiko import ConnectHandler


def backup_device(device_name, device, backup_folder, commands):
    print(f"Connecting to {device_name}...")

    connection = None

    try:
        connection = ConnectHandler(**device)

        device_folder = backup_folder / device_name
        device_folder.mkdir(parents=True, exist_ok=True)

        for command in commands:
            output = connection.send_command(command)

            filename = command.replace(" ", "_").upper() + ".txt"
            file_path = device_folder / filename

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(output)

        print(f"Backup completed for {device_name}")
        return True, None

    except Exception as error:
        print(f"Backup failed for {device_name}: {error}")
        return False, str(error)

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception as error:
                print(f"Warning: disconnect failed for {device_name}: {error}")

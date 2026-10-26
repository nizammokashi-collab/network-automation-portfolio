

from netmiko import ConnectHandler

def backup_device(device_name, device, backup_folder, commands):

    print(f"Connecting to {device_name}...")

    try:
        connection = ConnectHandler(**device)

        device_folder = backup_folder / device_name
        device_folder.mkdir(exist_ok=True)

        for command in commands:

            output = connection.send_command(command)

            filename = command.replace(" ", "_").upper() + ".txt"
            file_path = device_folder / filename
            with open(file_path, "w") as file:
                file.write(output)

        connection.disconnect()

        print(f"Backup completed for {device_name}")
        return True, None

    except Exception as error:
        print(f"Failed to connect to {device_name}")
        return False, str(error)

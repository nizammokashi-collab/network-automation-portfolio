
from netmiko import ConnectHandler
import logging

logger = logging.getLogger(__name__)

def backup_device(device_name, device, backup_folder, commands):
    logger.info("Connecting to %s...", device_name)

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

        logger.info("Backup completed for %s", device_name)
        return True, None

    except Exception as error:
        logger.exception("Backup failed for %s", device_name)
        return False, str(error)

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception as error:
                logger.warning("Disconnect failed for %s: %s", device_name, error)


import logging
import re

from netmiko import ConnectHandler

logger = logging.getLogger(__name__)

REQUIRED_DEVICE_FIELDS = (
    "device_type",
    "host",
    "username",
    "password",
)


def validate_device(device):
    """Validate required inventory fields before connecting."""
    if not isinstance(device, dict):
        raise ValueError("Device configuration must be a dictionary")

    for field in REQUIRED_DEVICE_FIELDS:
        value = device.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Missing or invalid required device field: {field}"
            )


def backup_device(device_name, device, backup_folder, commands):
    """Back up device command output and report any failures."""
    try:
        validate_device(device)

        if not commands:
            raise ValueError("No backup commands configured")

    except ValueError as error:
        logger.error("Invalid configuration for %s: %s", device_name, error)
        return False, str(error)

    logger.info("Connecting to %s...", device_name)
    connection = None
    failed_commands = []

    try:
        connection = ConnectHandler(**device)

        device_folder = backup_folder / device_name
        device_folder.mkdir(parents=True, exist_ok=True)

        for command in commands:
            try:
                logger.info(
                    "Running command '%s' on %s",
                    command,
                    device_name,
                )

                output = connection.send_command(command)

                # Generate a safe, predictable filename.
                filename = re.sub(
                    r"[^A-Za-z0-9_.-]+",
                    "_",
                    command.strip(),
                ).strip("._")

                if not filename:
                    filename = "backup_command"

                file_path = device_folder / f"{filename.upper()}.txt"

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(output)

                logger.info(
                    "Saved output for '%s' on %s",
                    command,
                    device_name,
                )

            except Exception as error:
                failed_commands.append(command)
                logger.exception(
                    "Command or file operation failed for '%s' on %s",
                    command,
                    device_name,
                )

        if failed_commands:
            error_message = (
                "Backup incomplete. Failed commands: "
                + ", ".join(failed_commands)
            )
            logger.error("%s: %s", device_name, error_message)
            return False, error_message

        logger.info("Backup completed successfully for %s", device_name)
        return True, None

    except Exception as error:
        logger.exception("Backup connection/setup failed for %s", device_name)
        return False, str(error)

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception:
                logger.exception("Disconnect failed for %s", device_name)

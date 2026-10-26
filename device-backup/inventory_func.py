from pathlib import Path
import yaml


def load_inventory():
    """Load device inventory from the local YAML file."""

    inventory_path = Path(__file__).resolve().parent / "Labs" / "devices.yaml"

    with open(inventory_path, "r", encoding="utf-8") as file:
        devices = yaml.safe_load(file)

    return devices
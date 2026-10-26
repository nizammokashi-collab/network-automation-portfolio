
from datetime import datetime
from pathlib import Path

def create_backup_folder():

    now = datetime.now()
    # Dynamic file
    backup_folder = (
        Path("backups")
        / now.strftime("%Y")
        / now.strftime("%m-%b")
        / now.strftime("%d")
        / now.strftime("%H-%M-%S")
    )
    backup_folder.mkdir(parents=True, exist_ok=True)

    return backup_folder

import json
from src.helpers.logger import logger
from src.helpers.config import config

"""
The config should look like so:

[
    {
        "id": "test1",
        "local": "/home/maxi/test1",
        "remote": "test_remote:/test1",
        "type": "onedrive"
    },
    {
        "id": "test2",
        "local": "/home/maxi/test2",
        "remote": "test_remote:/test2",
        "type": "onedrive"
    }
]
"""

class ConfigEntry:
    def __init__(self, id, local, remote, type):
        self.id = id
        self.local = local
        self.remote = remote
        self.type = type


class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    def __len__(self) -> int:
            return len(self.config_data)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                logger.debug(f"Loaded {self.config_file}")
                return json.load(file)
        except FileNotFoundError:
            logger.error("The rclone config file to manage sync destinations does not exist!")
            return []

    def save_config(self):
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config_data, file, indent=2)
                logger.debug(f"Saved config to {self.config_file}")
        except Exception as ex:
            logger.exception("Failed saving config:", ex)

    def add(self, id: str, local: str, remote: str, type):
        try:
            if not any(entry.get("id") == id for entry in self.config_data):
                if local.startswith("/"):
                    local = local[1:]
                new_entry = {"id": id, "local": local, "remote": remote, "type": type}
                self.config_data.append(new_entry)
                self.save_config()
                logger.info(f"Entry with id '{id}' added successfully.")
            else:
                logger.error(f"Entry with id '{id}' already exists. Cannot add duplicate entry.")
        except Exception as ex:
            logger.exception("Failed adding rclone sync destination:", ex)

    def delete(self, id):
        try:
            entries_to_remove = [entry for entry in self.config_data if entry.get("id") == id]
            for entry in entries_to_remove:
                self.config_data.remove(entry)
            self.save_config()
            logger.info(f"Entry with id '{id}' deleted successfully.")
        except Exception as ex:
            logger.exception(f"Failed deleting {id}:", ex)

    def get(self, id) -> ConfigEntry:
        try:
            entries = [ConfigEntry(**entry) for entry in self.config_data if entry.get("id") == id]
            return entries[0] if entries else None
        except Exception as ex:
            logger.exception(f"Failed getting config item: {ex}")

RcloneConfig = ConfigManager("src/configs/onedrive_sync_config.json")

logger.debug(f"Loaded {__name__} module")

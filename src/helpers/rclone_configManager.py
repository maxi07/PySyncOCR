import json
from src.helpers.logger import logger
from src.helpers.config import config
import os

"""
The config should look like so:

[
    {
        "id": "test1",
        "local": "/home/maxi/test1",
        "remote": "test1:/test1",
        "type": "onedrive"
    },
    {
        "id": "test2",
        "local": "/home/maxi/test2",
        "remote": "test2:/test2",
        "type": "onedrive"
    }
]
"""


class ConfigEntry:
    def __init__(self, id: str, local: str, remote: str, type):
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
        except json.decoder.JSONDecodeError:
            logger.error("The config file is broken.")
            quit()
        except Exception as ex:
            logger.exception(f"Failed loading config from {self.config_file}: {ex}")
            quit()

    def save_config(self):
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config_data, file, indent=2)
                logger.debug(f"Saved config to {self.config_file}")
        except Exception as ex:
            logger.exception("Failed saving config:", ex)

    def add(self, local: str, remote: str, connection: str, type="onedrive") -> bool:
        try:
            id = local
            if not any(entry.get("id") == id for entry in self.config_data):
                remotepath = connection + remote
                if local.startswith("/"):
                    local = local[1:]
                new_entry = {"id": id, "local": local, "remote": remotepath, "type": type}

                # Add new smb folder
                try:
                    os.makedirs(os.path.join(config.get_filepath("smb_service.share_path"), local), exist_ok=True)
                    logger.info(f"Created folder {os.path.join(config.get_filepath('smb_service.share_path'),local)}")
                except Exception as ex:
                    logger.exception(f"Failed creating folder {os.path.join(config.get_filepath('smb_service.share_path'),local)}:", ex)
                    return False
                self.config_data.append(new_entry)
                self.save_config()
                logger.info(f"Entry with id '{id}' added successfully.")
                return True
            else:
                logger.error(f"Entry with id '{id}' already exists. Cannot add duplicate entry.")
                return False
        except Exception as ex:
            logger.exception("Failed adding rclone sync destination:", ex)
            return False

    def delete(self, id) -> bool:
        try:
            entries_to_remove = [entry for entry in self.config_data if entry.get("id") == id]
            if len(entries_to_remove) == 0:
                logger.error(f"Entry with id '{id}' does not exist in database.")
            else:
                for entry in entries_to_remove:
                    self.config_data.remove(entry)
            self.save_config()
            try:
                os.removedirs(os.path.join(config.get_filepath("smb_service.share_path"), entry.get("local")))
                logger.info(f"Deleted folder {os.path.join(config.get_filepath('smb_service.share_path'),entry.get('local'))}")
            except OSError as oser:
                if oser.errno == 2:
                    logger.error(f"Folder {os.path.join(config.get_filepath('smb_service.share_path'),entry.get('local'))} does not exist.")
                elif oser.errno == 39:
                    logger.error(f"Folder {os.path.join(config.get_filepath('smb_service.share_path'),entry.get('local'))} is not empty.")
                else:
                    logger.exception(f"Failed deleting folder {os.path.join(config.get_filepath('smb_service.share_path'),entry.get('local'))}: {oser}")
                    return False
            except Exception as ex:
                logger.exception(f"Failed deleting folder {os.path.join(config.get_filepath('smb_service.share_path'),entry.get('local'))}: {ex}")
                return False
            logger.info(f"Entry with id '{id}' deleted successfully.")
            return True
        except Exception as ex:
            logger.exception(f"Failed deleting {id}:", ex)
            return False

    def get(self, id) -> ConfigEntry:
        try:
            entries = [ConfigEntry(**entry) for entry in self.config_data if entry.get("id") == id]
            return entries[0] if entries else None
        except Exception as ex:
            logger.exception(f"Failed getting config item: {ex}")


RcloneConfig = ConfigManager("src/configs/onedrive_sync_config.json")

logger.debug(f"Loaded {__name__} module")

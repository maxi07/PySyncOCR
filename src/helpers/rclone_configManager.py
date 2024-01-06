import json
from src.helpers.logger import logger

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

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
        except Exception as ex:
            logger.exception("Failed saving config:", ex)

    def add(self, id, local, remote, type):
        try:
            if not any(entry.get("id") == id for entry in self.config_data):
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

    def get(self, id):
        return [entry for entry in self.config_data if entry.get("id") == id]

# Example usage:
RcloneConfig = ConfigManager("src/configs/onedrive_sync_config.jso")

# Add an entry
RcloneConfig.add("test3", "/home/maxi/test3", "test_remote:/test3", "onedrive")

# Try to add a duplicate entry (it will print a message indicating that it already exists)
RcloneConfig.add("test3", "/home/maxi/test4", "test_remote:/test4", "onedrive")

# Remove an entry by id
RcloneConfig.delete("test2")

# Access the updated config data
print(RcloneConfig.config_data)

# Get entries by id
entries = RcloneConfig.get("test1")
print(entries)
logger.debug(f"Loaded {__name__} module")

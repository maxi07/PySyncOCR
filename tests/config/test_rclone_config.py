import pytest
from shutil import copy, move
from helpers.logger import logger
from helpers.rclone_configManager import ConfigManager
from helpers.config import config


@pytest.fixture
def use_backup():
    copy("src/configs/onedrive_sync_config.json", "src/configs/onedrive_sync_config.json.backup")
    logger.debug("Created backup of config.")
    yield
    move("src/configs/onedrive_sync_config.json.backup", "src/configs/onedrive_sync_config.json")
    logger.debug("Reverted to original config.")


@pytest.fixture
def onedrive_conf_setup():
    # Setup
    config_file = str(config.get("sync_service.root_folder"))
    rclone_config = ConfigManager(config_file)
    rclone_config.add("test1", "test1", "test2")

    # Return the configured instance
    return rclone_config


def test_duplicate(use_backup, onedrive_conf_setup):
    onedrive_conf_setup.add("test1", "test1:", "onedrive")

    # assert os.path.exists("$home/PySyncOCR/test1")
    assert len(onedrive_conf_setup) == 1


def test_delete(use_backup, onedrive_conf_setup):
    onedrive_conf_setup.delete("test1")
    assert len(onedrive_conf_setup) == 0

import pytest
from shutil import copy, move
from src.helpers.logger import logger
from src.helpers.rclone_configManager import ConfigManager
from src.helpers.config import config
import os

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

    # Assert
    # assert os.path.exists(f"{config.get('sync_service.root_folder')}/{local}")

    # Return the configured instance
    return rclone_config

def test_add(use_backup, onedrive_conf_setup):
    id = "test1"
    local = "test1"
    remote = "test2:test1/"
    type = "onedrive"

    # assert os.path.exists("$home/PySyncOCR/test1")
    test_item = onedrive_conf_setup.get("test1")
    assert test_item.id == id
    assert test_item.local == local
    assert test_item.remote == remote
    assert test_item.type == type


def test_duplicate(use_backup, onedrive_conf_setup):
    id = "test1"
    local = "test1"
    remote = "test1:test1/"
    type = "onedrive"

    onedrive_conf_setup.add("test1", "test1:", "onedrive")

    # assert os.path.exists("$home/PySyncOCR/test1")
    assert len(onedrive_conf_setup) == 1


def test_delete(use_backup, onedrive_conf_setup):
    onedrive_conf_setup.delete("test1")
    assert len(onedrive_conf_setup) == 0
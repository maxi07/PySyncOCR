import pytest
from shutil import copy, move
from helpers.logger import logger


@pytest.fixture
def use_backup():
    copy("src/configs/onedrive_sync_config.json", "src/configs/onedrive_sync_config.json.backup")
    logger.debug("Created backup of config.")
    yield
    move("src/configs/onedrive_sync_config.json.backup", "src/configs/onedrive_sync_config.json")
    logger.debug("Reverted to original config.")


def test_config_get(use_backup):
    from helpers.config import config
    assert config.get("sync_service.root_folder") == "PySyncOCR"


def test_config_getfilepath(use_backup):
    from helpers.config import config
    import os.path
    assert config.get_filepath("sync_service.original_dir") == os.path.expanduser("~/PySyncOCR/original")

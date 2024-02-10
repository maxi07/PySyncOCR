import pytest
from src.helpers.config import Config
from src.helpers.logger import logger
from shutil import copy, move
import re


@pytest.fixture(autouse=True)
def use_backup():
    copy("src/configs/onedrive_sync_config.json", "src/configs/onedrive_sync_config.json.backup")
    copy("src/configs/config.json", "src/configs/config.json.backup")
    logger.debug("Created backup of config.")
    yield
    move("src/configs/config.json.backup", "src/configs/config.json")
    move("src/configs/onedrive_sync_config.json.backup", "src/configs/onedrive_sync_config.json")
    logger.debug("Reverted to original config.")


def looks_like_path(path):
    # Define regular expression patterns for common path formats
    path_patterns = [
        r"^(?:[a-zA-Z]\:|\\\\[\w\.]+\\[\w.$]+)\\(?:[\w]+\\)*\w([\w.])+",
        r"^\/(?:[^\/]+\/)*[^\/]+$"  # Unix-like path
    ]

    # Check if the given string matches any of the path patterns
    for pattern in path_patterns:
        if re.match(pattern, path):
            return True
    return False


@pytest.fixture()
def conf_setup():
    conf = Config("src/configs/config.json")
    return conf


def test_len(conf_setup):
    assert len(conf_setup) > 0


def test_iter(conf_setup):
    assert len(conf_setup) > 0
    for k, v in conf_setup:
        assert k is not None
        assert v is not None


def test_get(conf_setup):
    assert conf_setup.get("sync_service.root_folder") == "PySyncOCR"


def test_get_empty(conf_setup):
    assert conf_setup.get("sync_service.root_folder.does_not_exist") is None


def test_get_filepath(conf_setup):
    assert looks_like_path(conf_setup.get_filepath("sync_service.root_folder")) is True


def test_set(conf_setup):
    conf_setup.set("sync_service.root_folder", "new_root_folder")
    assert conf_setup.get("sync_service.root_folder") == "new_root_folder"


def test_attr(conf_setup):
    assert type(conf_setup.get("sync_service.root_folder")) == str
    assert type(conf_setup.get("sync_service.keep_original")) == bool


def test_config_getfilepath(use_backup):
    from src.helpers.config import config
    import os.path
    assert config.get_filepath("sync_service.original_dir") == os.path.expanduser("~/PySyncOCR/original")

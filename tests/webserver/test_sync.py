import pytest
from src.webserver import create_app
from src.helpers.logger import logger
from shutil import copy, move
from bs4 import BeautifulSoup


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def use_backup():
    copy("src/configs/onedrive_sync_config.json", "src/configs/onedrive_sync_config.json.backup")
    copy("src/configs/config.json", "src/configs/config.json.backup")
    logger.debug("Created backup of config.")
    yield
    move("src/configs/config.json.backup", "src/configs/config.json")
    move("src/configs/onedrive_sync_config.json.backup", "src/configs/onedrive_sync_config.json")
    logger.debug("Reverted to original config.")


def test_index(client, use_backup):
    response = client.get('/sync', follow_redirects=True)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.h1.string == 'Sync'
    assert soup.title.string == "PySyncOCR"

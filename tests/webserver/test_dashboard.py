import pytest
from src.webserver import create_app
from src.helpers.logger import logger
from shutil import copy, move
from bs4 import BeautifulSoup
import re


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
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.h1.string == 'Dashboard'
    assert soup.title.string == "PySyncOCR"
    # Find the anchor tag with class 'nav-link active' and 'Dashboard' text
    dashboard_link_active = soup.find('a', class_='nav-link active', string='Dashboard')

    # Assert that the anchor tag is found
    assert dashboard_link_active is not None

    # This assert only works if we setup testing dbs
    # assert soup.find(string=re.compile("There is nothing to see here yet until you start scanning your first PDF."))

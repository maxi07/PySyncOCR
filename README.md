[![Pytest](https://github.com/maxi07/PySyncOCR/actions/workflows/pytest.yml/badge.svg)](https://github.com/maxi07/PySyncOCR/actions/workflows/pytest.yml)

<img src="src/webserver/static/images/PySyncOCR_logos_white.png#gh-dark-mode-only" width="30%">
<img src="src/webserver/static/images/PySyncOCR_logos_black.png#gh-light-mode-only" width="30%">

Welcome to PySyncOCR, a Python app that will
- Create a SMB server with custom targets
- OCR any new document in ENG and GER
- Sync your document to a location of choice within your OneDrive
- Have you let multiple sync targets

## Installation
Please clone the repo and run the `install.sh` with sudo privileges. This will create a service that automatically starts when the server boots and runs the `main.py`, which will launch different threads for the webserver, the watchdog, the SMB server and the OCR.

## Development
For developing we can use the built-in Flask server. To get debug output and use flask, run the `main.py` from VSCode with the `--dev` option or use the preconfigured launch.json.

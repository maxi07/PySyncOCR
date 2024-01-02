import os
import zipfile
import requests
import tempfile
import shutil
from src.logger import logger
import winreg


def download_file(url, destination) -> bool:
    try:
        response = requests.get(url)
        logger.debug(f"Received response code: {response.status_code}")
        with open(destination, 'wb') as file:
            file.write(response.content)
        return True
    except Exception:
        logger.exception("Failed downloading pngquant.")
        return False


def extract_zip(zip_path, extract_path) -> bool:
    logger.debug(f"Extracting {zip_path} to {extract_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        return True
    except Exception:
        logger.exception("Failed extracting zip.")
        return False


def add_path_to_system_env_variable(path):
    key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            current_path, _ = winreg.QueryValueEx(key, 'Path')
            new_path = f"{path};{current_path}"
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
    except PermissionError:
        logger.error("Failed adding pngquant to PATH, please run as administrator.")
    except Exception:
        logger.exception("Failed adding pngquant to system PATH.")


def install_pngquant():
    logger.info("Downloading and installing pngquant.")
    download_url = "https://pngquant.org/pngquant-windows.zip"
    temp_dir = tempfile.mkdtemp()
    zip_file_path = os.path.join(temp_dir, "pngquant-windows.zip")
    extract_path = os.path.join(os.getenv('APPDATA'))
    logger.debug(f"Downloading pngquant from {download_url} to {zip_file_path}")

    try:
        # Download the file
        res = download_file(download_url, zip_file_path)
        if not res:
            return

        # Extract contents to %APPDATA%\pngquant
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
            logger.debug(f"Created temp dir at {temp_dir}")
        res = extract_zip(zip_file_path, extract_path)
        if not res:
            return

        # Delete the downloaded zip file
        try:
            os.remove(zip_file_path)
        except Exception:
            logger.exception("Failed removing temporary zip.")

        # Add pngquant.exe path to Environment Variables
        res = add_path_to_system_env_variable(os.path.join(extract_path, 'pngquant'))
        if not res:
            return

        logger.info("Setup for pngquant completed successfully.")

    except Exception:
        logger.exception("An error occurred during install of pngquant.")

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    install_pngquant()

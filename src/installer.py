import platform
from src.logger import logger
import sys
import os
import subprocess
from win32api import GetFileVersionInfo, LOWORD, HIWORD
from src.config import config
from src.helpers.install_pngquant import install_pngquant


def check_install():
    # Test for complete installation
    if platform.system() == 'Windows':
        logger.debug("Running on Windows")

        # Test tesseract
        if not os.path.exists(config.get("setup.windows.tesseract_path")):
            logger.warning("Unable to detect tesseract.")
            install_tesseract_windows()
        logger.debug(f"Detected tesseract version {get_version_number_windows(config.get("setup.windows.tesseract_path"))}")

        # Test Ghostscript
        if not os.path.exists(config.get("setup.windows.ghostscript_path")):
            logger.warning("Unable to detect Ghostscript.")
            logger.warning("Please install ghostscript from https://ghostscript.com/releases/gsdnld.html")
            sys.exit(-1)
        logger.debug(f"Detected ghostscript version {get_version_number_windows(config.get("setup.windows.ghostscript_path"))}")

        # Test pngquant
        if not os.path.exists(os.path.join(os.getenv('APPDATA'), config.get("setup.windows.pngquant_path"))):
            logger.warning(f"Unable to detect pngquant at {os.path.join(os.getenv('APPDATA'), config.get("setup.windows.pngquant_path"))}")
            install_pngquant()
        logger.debug(f"Detected pngquant version {get_version_number_windows(config.get("setup.windows.pngquant_path"))}")

    elif platform.system() == 'Linux':
        logger.debug("Running on Linux")
        installed, output = is_ocrmypdf_installed_linux()
        if not installed():
            logger.info("OCRmyPDF is not detected, attempting install")
            install_ocrmypdf_linux()
        logger.debug(f"Detected ocrmypdf version {output}")
    else:
        logger.debug("Running on a different operating system")
        logger.error("OS is not supported.")
        sys.exit(-1)


def get_version_number_windows(filename) -> str:
    try:
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{HIWORD(ms)}.{LOWORD(ms)}.{HIWORD(ls)}.{LOWORD(ls)}"
    except Exception:
        return "Unknown version"


def install_tesseract_windows():
    logger.info("Downloading tesseract for Windows.")
    package_id = "UB-Mannheim.TesseractOCR"

    try:
        subprocess.run(["winget", "install", "-e", "--id", package_id], check=True)
        logger.info(f"Package {package_id} installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing package {package_id}. Return code: {e.returncode}")
        logger.error(f"Error output: {e.output.decode()}")
        logger.info("Please install tesseract manually using https://ub-mannheim.github.io/Tesseract_Dokumentation/Tesseract_Doku_Windows.html")
        sys.exit(-1)


def install_ocrmypdf_linux():
    package_name = "ocrmypdf"

    try:
        subprocess.run(["sudo", "apt", "install", package_name], check=True)
        logger.info(f"Package {package_name} installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing package {package_name}. Return code: {e.returncode}")
        logger.error(f"Error output: {e.output.decode()}")


def is_ocrmypdf_installed_linux():
    try:
        result = subprocess.run(["ocrmypdf", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        output = result.stdout.decode('utf-8').strip()
        return True, output
    except FileNotFoundError:
        return False, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode('utf-8').strip()


def install_pngquant_windows():
    install_pngquant()


logger.debug("Started installer module")
if __name__ == "__main__":
    check_install()

import platform
from src.helpers.logger import logger
import sys
import subprocess

def check_install():
    """
    Check the installation status of OCRmyPDF and RClone on a Linux system.
    If not installed, attempt to install and log the version information.
    """
    if platform.system() != 'Linux':
        logger.debug("Running on a different operating system")
        logger.error("OS is not supported.")
        sys.exit(-1)

    logger.debug("Running on Linux")

    check_and_install("python3", "python3")
    check_and_install("pip", "pip")
    check_and_install("OCRmyPDF", "ocrmypdf")
    check_and_install("RClone", "rclone")


def check_and_install(tool_name, package_name):
    """
    Check if a tool is installed on a Linux system.
    If not installed, attempt to install and log the version information.

    Parameters:
    - tool_name (str): The name of the tool for logging purposes.
    - package_name (str): The name of the package/tool to check and install.
    """
    installed, output = is_installed_linux(package_name)
    
    if not installed:
        logger.info(f"{tool_name} is not detected, attempting install")
        install_package_linux(package_name)
        output = subprocess.run([package_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8').strip().split('\n')[0]
    
    logger.debug(f"Detected {tool_name} version {output}")


def install_package_linux(package_name):
    """
    Install a package/tool on a Linux system using the apt package manager.

    Parameters:
    - package_name (str): The name of the package/tool to install.
    """
    try:
        subprocess.run(["sudo", "apt", "update", "-y"], check=True)
        subprocess.run(["sudo", "apt", "install", package_name, "-y"], check=True)
        logger.info(f"Package {package_name} installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing package {package_name}. Return code: {e.returncode}")


def is_installed_linux(tool_name):
    """
    Check if a tool is installed on a Linux system.

    Parameters:
    - tool_name (str): The name of the tool to check.

    Returns:
    - Tuple: A tuple containing a boolean indicating if the tool is installed,
             and the version information if available.
    """
    try:
        result = subprocess.run([tool_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8').strip().split('\n')[0]
        return True, result
    except FileNotFoundError:
        return False, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode('utf-8').strip()


logger.debug(f"Loaded {__name__} module")

if __name__ == "__main__":
    check_install()

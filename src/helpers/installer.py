import platform
import re
from src.helpers.logger import logger
import sys
import subprocess
import os
import stat


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
    check_and_install("Tesseract German Language Pack", "tesseract-ocr-deu", True)
    check_and_install("RClone", "rclone")
    check_and_install("autotools-dev", "autotools-dev", True)
    check_and_install("automake", "automake")
    check_and_install("libtool", "libtool", True)
    check_and_install("libleptonica-dev", "libleptonica-dev", True)
    check_and_install("samba", "samba")
    check_jbig2()


def check_and_install(tool_name, package_name, is_package=False):
    """
    Check if a tool is installed on a Linux system.
    If not installed, attempt to install and log the version information.

    Parameters:
    - tool_name (str): The name of the tool for logging purposes.
    - package_name (str): The name of the package/tool to check and install.
    """
    installed, output = is_installed_linux(package_name, is_package)

    if not installed:
        logger.warning(f"{tool_name} is not detected, attempting install")
        # install_package_linux(package_name)
        try:
            installed, output = is_installed_linux(package_name, is_package)
            if not installed:
                logger.error(f"Error installing {tool_name}")
                output = "Unknown"
        except Exception as e:
            logger.exception(f"Error installing {tool_name}: {e}")
            output = "Unknown"

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


def is_installed_linux(tool_name, is_package=False):
    """
    Check if a tool is installed on a Linux system.

    Parameters:
    - tool_name (str): The name of the tool to check.

    Returns:
    - Tuple: A tuple containing a boolean indicating if the tool is installed,
             and the version information if available.
    """
    try:
        if is_package:
            result = subprocess.run(["dpkg", "-s", tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode('utf-8')
            # Define a regular expression to match the version number
            version_pattern = re.compile(r"Version:\s+(\S+)")

            # Find the version number in the sample output
            match = version_pattern.search(result)

            # Check if a match is found
            if match:
                result = match.group(1)
            else:
                logger.warning(f"Version number not found in the sample output for {tool_name}.")
        else:
            result = subprocess.run([tool_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            version = result.stdout.decode('utf-8').strip().split('\n')[0]
            if version is None or len(version) == 0:
                version = result.stderr.decode('utf-8').strip().split('\n')[0]
            result = version if version is not None else "unknown"
        return True, result
    except FileNotFoundError:
        return False, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode('utf-8').strip()


def check_jbig2():
    installed, output = is_installed_linux("jbig2")
    if not installed:
        logger.warning("JBIG2 is not installed, attempting install")
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'install_jbig2.sh')
            logger.debug(f"Installing JBIG2 from {script_path}")
            st = os.stat(script_path)
            logger.debug(f"Setting permissions on {script_path}")
            os.chmod(script_path, st.st_mode | stat.S_IEXEC)
            logger.debug(f"Running {script_path}")
            result = subprocess.run([script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(result.stdout.decode('utf-8').strip())
            logger.info("Successfully installed JBIG2")
        except subprocess.CalledProcessError as e:
            logger.error(e.stderr.decode('utf-8').strip())

    installed, output = is_installed_linux("jbig2")
    if installed:
        logger.debug(f"Detected JBIG2 version {output}")
    else:
        logger.warning("Unable to find JBIG2")


logger.debug(f"Loaded {__name__} module")

if __name__ == "__main__":
    check_install()

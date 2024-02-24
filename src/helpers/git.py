from src.helpers.run_subprocess import run_subprocess
from src.helpers.logger import logger

git_version = "Unknown"


def get_git_version():
    try:
        code, msg = run_subprocess(['git', 'describe', '--tags', '--abbrev=0'])
        if code == 0 and msg.startswith("v"):
            version = msg.split("v")[1]
        else:
            version = "Unknown"
    except Exception as e:
        logger.exception(f"Failed retrieving git version: {e}")
        version = "Unknown"
    finally:
        return version

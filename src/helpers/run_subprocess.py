import subprocess
from src.helpers.logger import logger


def run_subprocess(command: list[str], cwd=None) -> tuple[int, str]:
    """
    Run a subprocess and return the result.
    Returns code and stderr if fails, else returns code and stdout.
    """
    logger.debug(f"Calling {' '.join(command)}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, cwd=cwd)
        logger.debug(f"Received {result}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running subprocess: {e}")
        logger.error(e.stderr.decode())
        return e.returncode, e.stderr.decode().strip()
    return result.returncode, result.stdout.decode().strip()

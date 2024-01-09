from typing import List
from src.helpers.logger import logger
import subprocess
import json


def list_remotes() -> list[str]:
    """
    Retrieve a list of remotes configured in rclone.

    Returns:
    - list[str]: A list of remote names.

    Note:
    - Uses the 'rclone listremotes' command to get remote names.
    """
    command = ['rclone', 'listremotes']

    try:
        logger.debug(f"Calling {' '.join(command)}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.debug(f"Received {result}")

        # Split the input string by lines and remove empty lines
        lines = [line.strip() for line in result.stdout.decode().split('\n') if line.strip()]

        # Remove colons from each line
        result_list = [line.replace(':', '') for line in lines]
        logger.debug(f"Found remotes: {str(result_list)}")
        return result_list
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting remotes rclone: {e}")
        return []


def list_folders(connection: str, folder=None) -> list[str] | None:
    """
    List folders in a remote storage using rclone.

    Args:
        connection (str): The name or path of the remote storage connection.
        folder (str, optional): The path to the parent folder. Defaults to None.

    Returns:
        list[str] | None: A list of folder names if successful, or None if an error occurs.

    Raises:
        subprocess.CalledProcessError: If the underlying rclone command encounters an error.

    Notes:
        The function uses rclone to list folders in the specified remote storage connection.
        If `folder` is provided, it lists folders within that specific directory; otherwise,
        it lists folders in the root directory of the remote storage.

    Example:
        >>> list_folders("my_remote:")
        ['folder1', 'folder2']

    """
    if folder is None:
        command = ['rclone', 'lsf', connection, f"--dirs-only"]
        logger.debug(f"Calling {' '.join(command)}")
    else:
        command = ['rclone', 'lsf', connection + folder, f"--dirs-only"]
        logger.debug(f"Calling {' '.join(command)}")

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # Parse the JSON string into a list of dictionaries
        try:
            logger.debug("Received command result")
            lines = [line.strip() for line in result.stdout.decode().split('\n') if line.strip()]
            logger.debug("Folders: " + str(lines))
            return lines
        except json.JSONDecodeError as json_err:
            logger.error(f"Error decoding JSON: {json_err}")
            return None
    except subprocess.CalledProcessError as e:
        if e.returncode == 3:
            logger.error(f"The specified remote {connection} does not exist.")
            logger.error(e.stderr.decode())
        else:
            logger.error(f"Error getting filesandfolders rclone (Code {e.returncode}): {e}")
        return None


def create_folder(connection: str, path: str, foldername: str) -> bool:
    if not path.endswith("/"):
        path += "/"
    command = ['rclone', 'mkdir', connection + path + foldername]
    logger.debug(f"Calling {' '.join(command)}")

    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.info(f"Created new folder at {path + foldername}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating folder rclone: {e}")
        return False


def remove_folder(connection: str, path: str, foldername: str) -> bool:
    if not path.endswith("/"):
        path += "/"
    command = ['rclone', 'rmdir', connection + path + foldername]
    logger.debug(f"Calling {' '.join(command)}")

    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.info(f"Removed folder at {path + foldername}")
        return True
    except subprocess.CalledProcessError as e:
        if e.returncode == 3:
            logger.error(f"Directory {foldername} does not exist at {path}.")
        elif e.returncode == 1 and e.stderr.decode().endswith("directory not empty\n"):
            logger.error(f"Directory {foldername} at {path} cannot be deleted, as its not empty.")
        else:
            logger.error(f"Error removing folder at {path + foldername} rclone: {e}")
        return False
    

def upload_file(src_path: str, remote_path: str) -> bool:
    command = ['rclone', 'moveto', src_path, remote_path]
    logger.debug(f"Calling {' '.join(command)}")

    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.info(f"Uploaded file from {src_path } to {remote_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error uploading file from {src_path} to {remote_path}: {e}\n{e.stderr.decode()}")
        return False
    
logger.debug(f"Loaded {__name__} module")

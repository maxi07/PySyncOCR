from typing import List
from src.logger import logger
import subprocess
import json

class FileItem:
    def __init__(self, Path, Name, Size, MimeType, ModTime, IsDir, ID):
        self.path = Path
        self.name = Name
        self.size = Size
        self.mime_type = MimeType
        self.mod_time = ModTime
        self.is_dir = IsDir
        self.file_id = ID

    def __repr__(self):
        return f"FileItem(path={self.path}, name={self.name}, size={self.size}, mime_type={self.mime_type}, mod_time={self.mod_time}, is_dir={self.is_dir}, file_id={self.file_id})"


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
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.debug(f"Received {result}")

        # Split the input string by lines and remove empty lines
        lines = [line.strip() for line in result.stdout.decode().split('\n') if line.strip()]

        # Remove colons from each line
        result_list = [line.replace(':', '') for line in lines]
        return result_list
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting remotes rclone: {e}")
        return []


def list_filesandfolders(connection: str, folderid=None) -> List[FileItem] | None:
    command = ['rclone', 'lsjson', connection]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # Parse the JSON string into a list of dictionaries
        try:
            logger.debug("Received command result")
            items = json.loads(result.stdout.decode())
        except json.JSONDecodeError as json_err:
            logger.error(f"Error decoding JSON: {json_err}")
            return None

        # Create FileItem objects
        file_objects = [FileItem(**item) for item in items]
        return file_objects
    except subprocess.CalledProcessError as e:
        if e.returncode in (1):
            logger.error(f"The specified remote {connection} does not exist.")
        else:
            logger.error(f"Error getting filesandfolders rclone: {e}")
        return None

print(list_filesandfolders("test2:"))
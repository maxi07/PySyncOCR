from helpers.logger import logger
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
    command = ['rclone', 'listremotes', '--long']

    try:
        logger.debug(f"Calling {' '.join(command)}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.debug(f"Received {result}")

        # Split the input string by lines and remove empty lines
        lines = [line.strip() for line in result.stdout.decode().split('\n') if line.strip()]

        # Remove colons from each line
        filtered_list = [item for item in lines if ": onedrive" in item]
        result_list = [line.replace(': onedrive', '') for line in filtered_list]
        logger.debug(f"Found remotes: {str(result_list)}")
        return result_list
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting remotes rclone: {e}")
        return []


def list_folders(connection: str, folder=None) -> dict | None:
    if folder is None:
        command = ['rclone', 'lsf', connection, "--dirs-only", "--recursive", "--max-depth", "2"]
        logger.debug(f"Calling {' '.join(command)}")
    else:
        command = ['rclone', 'lsf', connection + folder, "--dirs-only", "--recursive", "--max-depth", "2"]
        logger.debug(f"Calling {' '.join(command)}")

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # Parse the JSON string into a list of dictionaries
        try:
            logger.debug("Received command result")
            lines = [line.strip() for line in result.stdout.decode().split('\n') if line.strip()]
            logger.debug(f"Received: {len(lines)} results")

            # Convert this list into a dict holding amount of subdirs
            # eg {'Anlagen': 0, 'AppData': 1}
            directory_dict = {}
            if len(lines) > 0:
                for item in lines:
                    parts = item.split("/")
                    top_level_directory = parts[0]

                    if top_level_directory not in directory_dict:
                        directory_dict[top_level_directory] = 0
                    else:
                        directory_dict[top_level_directory] += 1

            return directory_dict
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


def dump_config():
    command = ['rclone', 'config', 'dump']
    logger.debug(f"Calling {' '.join(command)}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        res = json.loads(result.stdout.decode())
        logger.debug(f"Received {len(res)} onedrive configs")
        return res
    except subprocess.CalledProcessError as e:
        logger.error(f"Error dumping rclone config: {e}")
        return None


def delete_config_item(id) -> bool:
    command = ['rclone', 'config', 'delete', id]
    logger.debug(f"Calling {' '.join(command)}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.debug(f"Received {result}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error deleting config item {id} rclone: {e}")
        return False


logger.debug(f"Loaded {__name__} module")

from src.helpers.logger import logger
from src.helpers.rclone_management_onedrive import list_remotes
from src.services.smb_server_alternative import SambaController
from src.webserver.db import send_database_request
from src.helpers.run_subprocess import run_subprocess
import json


def inject_template_data():
    # Test for errors in path mappings
    # Get path mappings
    try:
        mapping_error = False
        with open("src/configs/onedrive_sync_config.json", "r") as f:
            path_mappings = json.load(f)
            logger.debug(f"Loaded {len(path_mappings)} path mappings")

        # Check if the connection in the path mapping actually exisits
        for path_mapping in path_mappings:
            if str(path_mapping["remote"]).split(":")[0] not in list_remotes():
                logger.warning(f"Remote {str(path_mapping['remote']).split(':')[0]} not found in rclone remotes.")
                logger.debug("Set mapping_error to True to display warning in Navbar")
                mapping_error = True
    except Exception as e:
        logger.exception(f"Failed looking for binding errors: {e}")

    # Count failed documents
    try:
        res = send_database_request(r"SELECT COUNT(*) FROM scanneddata WHERE LOWER(file_status) LIKE '%failed%'")
        failed_documents = int(res[0][0])
    except Exception as e:
        logger.exception(f"Failed counting failed documents: {e}")
        failed_documents = 0

    # Check SMB status
    try:
        logger.debug("Checking SMB status...")
        smb_status = SambaController.check_is_running()
    except Exception as e:
        logger.exception(f"Failed checking SMB status: {e}")
        smb_status = False

    try:
        code, msg = run_subprocess(['git', 'describe', '--tags', '--abbrev=0'])
        if code == 0 and msg.startswith("v"):
            version = msg.split("v")[1]
        else:
            version = "Unknown"
    except Exception as e:
        logger.exception(f"Failed retrieving git version: {e}")
        version = "Unknown"

    template_data = {
        'mapping_error': mapping_error,
        'failed_documents': failed_documents,
        'smb_error': smb_status,
        'version': version
    }
    return template_data

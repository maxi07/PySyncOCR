import math
from flask import Blueprint, jsonify, render_template, request, send_file
bp = Blueprint('sync', __name__, url_prefix='/sync')
from src.helpers.logger import logger
from src.helpers.rclone_management_onedrive import dump_config, delete_config_item, list_remotes, list_folders
from src.helpers.rclone_setup import configure_rclone_onedrive_personal, check_ssh_enabled
from src.helpers.rclone_configManager import RcloneConfig
from . import socketio
from src.webserver.db import get_db
from src.helpers.config import config
import json
import os
import socket


@bp.route("/")
def index():
    """
    Renders the sync page by:

    - Loading the onedrive rclone configs with dump_config()
    - Loading the path mappings from a json file
    - Checking if the onedrive remotes in the mappings actually exist
    - Getting a paginated list of failed pdf sync jobs from the database
    - Passing all this data to the sync.html template

    If there are any errors, catches them and renders the template with empty data.
    """
    try:
        logger.info("Loading sync...")
        onedrive_configs = dump_config()

        # Get path mappings
        try:
            with open("src/configs/onedrive_sync_config.json", "r") as f:
                path_mappings = json.load(f)
                logger.debug(f"Loaded {len(path_mappings)} path mappings")

            # Check if the connection in the path mapping actually exisits
            for path_mapping in path_mappings:
                if str(path_mapping["remote"]).split(":")[0] not in list_remotes():
                    logger.warning(f"Remote {str(path_mapping['remote']).split(':')[0]} not found in rclone remotes.")
                    path_mapping["remote_exists"] = False
                else:
                    path_mapping["remote_exists"] = True
                    continue
        except Exception as e:
            logger.exception(e)
            path_mappings = {}

        # Get failed sync documents for table by checking all database
        try:
            db = get_db()
            page_failed_pdfs = request.args.get('page_failed_pdfs', 1, type=int)  # Get pageination from url args
            total_entries = db.execute('SELECT COUNT(*) FROM scanneddata WHERE LOWER(file_status) LIKE "%failed%"').fetchone()[0]
            entries_per_page = 20
            total_pages_failed_pdfs = math.ceil(total_entries / entries_per_page)
            offset = (page_failed_pdfs - 1) * entries_per_page
            failed_pdfs = db.execute(
                'SELECT *, DATETIME(created, "localtime") AS local_created, DATETIME(modified, "localtime") AS local_modified FROM scanneddata '
                'WHERE LOWER(file_status) LIKE "%failed%" '
                'ORDER BY created DESC '
                'LIMIT :limit OFFSET :offset',
                {'limit': entries_per_page, 'offset': offset}
            ).fetchall()
        except Exception as ex:
            logger.exception(f"Failed retrieving failed pdfs. {ex}")
            failed_pdfs = []

        try:
            hostname = socket.gethostname()
        except Exception as e:
            logger.exception(e)
            hostname = "unknown"

        return render_template('sync.html',
                               onedrive_configs=onedrive_configs,
                               path_mappings=path_mappings,
                               failed_pdfs=failed_pdfs,
                               total_pages_failed_pdfs=total_pages_failed_pdfs,
                               page_failed_pdfs=page_failed_pdfs,
                               hostname=hostname)
    except Exception as e:
        logger.exception(e)
        return render_template('sync.html',
                               onedrive_configs={},
                               path_mappings={},
                               failed_pdfs=[],
                               total_pages_failed_pdfs=0,
                               page_failed_pdfs=1,
                               hostname="unknown")


@bp.delete("/onedrive")
def deleteOneDriveConf():
    """Deletes an OneDrive configuration item based on the provided ID in the request body"""
    try:
        logger.info("Deleting onedrive config...")
        json_data = request.get_json()
        if not json_data:
            logger.warning("No data received!")
            return "No data received!", 400
        else:
            logger.info(f"Received data: {json_data}")
            if delete_config_item(json_data['id']):
                return f"Success deleting {json_data['id']}", 200
            else:
                return f"Failed deleting {json_data['id']}", 500
    except Exception as ex:
        logger.exception(ex)
        return "Failed deleting requested item", 500


@bp.get("/onedrive")
def getOneDriveRemotes():
    """Gets a list of configured OneDrive remotes.

    Returns:
        A JSON response with a list of configured OneDrive remotes, and a 200 OK status code.

    Raises:
        500 Server Error if there is an error retrieving the remotes. Logs the exception.
    """
    try:
        logger.info("Retrieving onedrive configs...")
        res = list_remotes()
        return jsonify(res), 200
    except Exception as ex:
        logger.exception(ex)
        return "Failed retrieving remotes", 500


@bp.post("/onedrive-directory")
def getOneDriveDirectories():
    """Retrieves the directories in a OneDrive path.

    Expects a JSON request with the 'remote_id' and 'path' of the OneDrive to retrieve directories from.
    Calls the list_folders function to get the directories.
    Logs and returns the list of directories if successful, error messages otherwise.
    Catches and logs any errors.
    """
    try:
        json_data = request.get_json()
        logger.info(f"Retrieving onedrive directory for {json_data}...")
        res = list_folders(json_data["remote_id"], json_data["path"])
        return res, 200
    except Exception as ex:
        logger.exception(ex)
        return "Failed retrieving remotes", 500


@socketio.on('connect', namespace='/websocket-onedrive')
def websocket_connect():
    logger.debug("Client connected to onedrive websocket")
    socketio.emit('message_update', 'Connected to onedrive websocket', namespace='/websocket-onedrive')


@socketio.on('disconnect', namespace='/websocket-onedrive')
def websocket_disconnect():
    logger.debug("Client disconnected from onedrive websocket")


@socketio.on('message_update', namespace='/websocket-onedrive')
def handle_message(message):
    """
    Handle realtime sync updates from rclone sent over a websocket.

    Accepts a websocket connection and json data containing the onedrive remote name.
    Calls configure_rclone_onedrive_personal to sync the remote, and sends back sync updates over the websocket.
    """
    if message is None:
        return
    else:
        logger.info(f"Received data: {message}")
        json_data = json.loads(message)
        socketio.emit('message_update', 'Connecting to OneDrive...', namespace='/websocket-onedrive')
        if "name" in json_data:
            socketio.start_background_task(target=configure_rclone_onedrive_personal, name=json_data["name"])


@bp.post("/pathmapping")
def addPathMapping():
    """Adds a path mapping between a local path and a remote path + remote ID.

    Takes a JSON request with the following data:
    - local_path: The local file path to map
    - remote_path: The remote path on the cloud storage to map to
    - remote_id: The ID of the remote cloud storage

    Returns 200 if successful along with a message, 500 if failed along with an error message.
    """
    try:
        json_data = request.get_json()
        if not json_data or "local_path" not in json_data or "remote_path" not in json_data or "remote_id" not in json_data:
            return "Missing required data in request", 400

        if not json_data["local_path"] or not json_data["remote_path"] or not json_data["remote_id"]:
            return "Values cannot be empty", 400

        logger.info(f"Received path mapping: {json_data}")
        res = RcloneConfig.add(json_data["local_path"], json_data["remote_path"], json_data["remote_id"])
        if res:
            return f"Added {json_data['local_path']} to mappings", 200
        else:
            return f"Failed adding {json_data['local_path']} to mappings", 500
    except Exception as ex:
        logger.exception(ex)
        return "Failed adding mapping. " + ex, 500


@bp.delete("/pathmapping")
def deletePathMapping():
    """Deletes a path mapping.

    Expects a JSON request with the 'id' of the mapping to delete.
    Logs and returns a message indicating whether the delete succeeded.
    Catches and logs any errors.
    """
    try:
        json_data = request.get_json()
        if not json_data or "id" not in json_data:
            return "Missing required data in request", 400
        logger.info(f"Received path mapping to delete: {json_data}")
        res = RcloneConfig.delete(json_data["id"])
        if res:
            return f"Deleted {json_data['id']} from mappings", 200
        else:
            return f"Failed deleting {json_data['id']} from mappings", 500
    except Exception as ex:
        logger.exception(ex)
        return "Failed deleting mapping. " + ex, 500


@bp.delete("/failedpdf")
def deleteFailedPDF():
    """Deletes a failed PDF file from the failed PDF directory.

    Expects a JSON request with the ID of the failed PDF to delete.
    Looks up the file name for the ID, deletes the file,
    and updates the database.

    Returns a success or error message.
    """
    db = get_db()
    try:
        json_data = request.get_json()
        if not json_data:
            logger.warning("No data received!")
            return "No data received!", 400
        else:
            logger.info(f"Received data to delete: {json_data}")

            item_name = db.execute(
                'SELECT file_name FROM scanneddata '
                'WHERE id = :id',
                {'id': json_data['id']}
            ).fetchone()[0]
            logger.info(f"Removing {os.path.join(config.get_filepath('sync_service.failed_dir'), item_name)}")
            os.remove(os.path.join(config.get_filepath("sync_service.failed_dir"), item_name))
            db = get_db()
            db.execute(
                f'UPDATE {config.get("sql.db_pdf_table")} SET file_status = :status, modified = CURRENT_TIMESTAMP WHERE id = :id',
                {'status': 'Deleted', 'id': json_data['id']}
            )
            db.commit()
            db.close()
            return f"Success deleting {item_name}", 200
    except Exception as ex:
        logger.exception(f"Error deleting file: {ex}")
        return "Failed deleting requested item", 500
    finally:
        db.close()


@bp.get("/failedpdf")
def downloadFailedPDF():
    """Downloads a failed PDF file for the given id from the failed PDF directory.
    Returns the file if it exists, handles invalid ids and other errors.

    Returns:
        File if it exists or error message
    """
    try:
        download_id = int(request.args.get('download_id'))
        if download_id is None or download_id <= 0:
            logger.warning(f"Downloading failed PDF with id {download_id}, invalid id")
            return "Invalid download id", 400
        logger.info(f"Downloading failed PDF... with id {download_id}")

        # Get name in os from sql db
        db = get_db()
        item_name = db.execute(
            'SELECT file_name FROM scanneddata '
            'WHERE id = :id',
            {'id': download_id}
            ).fetchone()[0]

        # Check if file exists
        file_path = os.path.join(config.get_filepath("sync_service.failed_dir"), item_name)
        logger.debug(f"Checking if file exists: {file_path}")
        if not os.path.isfile(file_path):
            logger.warning(f"Downloading failed PDF with id {download_id}, file does not exist")
            return "File does not exist", 404
        else:
            logger.info(f"Downloading failed PDF with id {download_id}, file exists")
            return send_file(file_path, as_attachment=True)
    except ValueError:
        logger.warning(f"Downloading failed PDF with id {download_id}, invalid id")
        return "Invalid download id", 400
    except Exception as ex:
        logger.exception(f"Failed downloading PDF: {ex}")
        return "Failed downloading PDF", 500


@bp.get("/check-ssh")
def checkSSH():
    """Checks if SSH is enabled and active."""

    res = check_ssh_enabled()
    if res == 0:
        return "SSH is enabled and active.", 200
    elif res == -1:
        return "SSH is not installed.", 500
    elif res == -2:
        return "SSH is not active.", 500
    elif res == -3:
        return "SSH is not enabled.", 500
    else:
        return "Unknown error", 500

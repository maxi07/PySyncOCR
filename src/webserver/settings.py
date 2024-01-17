from flask import Blueprint, jsonify, render_template, request, redirect
bp = Blueprint('settings', __name__, url_prefix='/settings')
from src.helpers.logger import logger
from src.helpers.rclone_management_onedrive import dump_config, delete_config_item, list_remotes, list_folders
from src.helpers.rclone_setup import configure_rclone_onedrive_personal
from src.helpers.rclone_configManager import RcloneConfig
from . import sock
import json

@bp.route("/")
def index():
    try:
        logger.info("Loading settings...")
        onedrive_configs = dump_config()
        try:
            with open("src/configs/onedrive_sync_config.json", "r") as f:
                path_mappings = json.load(f)
                logger.debug(f"Loaded {len(path_mappings)} path mappings")

        except Exception as e:
            logger.exception(e)
            path_mappings = {}
        return render_template('settings.html',
                               onedrive_configs=onedrive_configs,
                               path_mappings=path_mappings)
    except Exception as e:
        logger.exception(e)
        return render_template('settings.html',
                               onedrive_configs={},
                               path_mappings={})
    
@bp.delete("/onedrive")
def deleteOneDriveConf():
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
    try:
        logger.info("Retrieving onedrive configs...")
        res = list_remotes()
        return jsonify(res), 200
    except Exception as ex:
        logger.exception(ex)
        return "Failed retrieving remotes", 500
    
@bp.post("/onedrive-directory")
def getOneDriveDirectories():
    try:
        json_data = request.get_json()
        logger.info(f"Retrieving onedrive directory for {json_data}...")
        res = list_folders(json_data["remote_id"], json_data["path"])
        return res, 200
    except Exception as ex:
        logger.exception(ex)
        return "Failed retrieving remotes", 500

    
@sock.route("/websocket-onedrive")
def websocket(ws):
    while True:
        data = ws.receive()
        if data is None:
            break
        else:
            logger.info(f"Received data: {data}")
            json_data = json.loads(data)
            if "name" in json_data:
                try:
                    for update in configure_rclone_onedrive_personal(json_data["name"]):
                        logger.debug(f"Received signal from rclone: {update}")
                        if update.startswith("http"):
                            ws.send(update)
                        elif update == "0":
                            ws.send("Success: " + update)
                        else:
                            ws.send("Failed: " + update)
                except StopIteration as e:
                    ws.send("An error occured: " + str(e.value) + "\n Please try again later.")
            else:
                ws.send("Failed - cant handle this.")


@bp.post("/pathmapping")
def addPathMapping():
    try:
        json_data = request.get_json()
        if not json_data or "local_path" not in json_data or "remote_path" not in json_data or "remote_id" not in json_data:
            return "Missing required data in request", 400
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
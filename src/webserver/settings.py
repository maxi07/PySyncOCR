from flask import Blueprint, render_template, request, redirect
bp = Blueprint('settings', __name__, url_prefix='/settings')
from src.helpers.logger import logger
from src.helpers.rclone_management_onedrive import dump_config, delete_config_item
from src.helpers.rclone_setup import configure_rclone_onedrive_personal
from . import sock
import json

@bp.route("/")
def index():
    try:
        logger.info("Loading settings...")
        onedrive_configs = dump_config()
        return render_template('settings.html', onedrive_configs=onedrive_configs)
    except Exception as e:
        logger.exception(e)
        return render_template('settings.html', onedrive_configs=[])
    
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
            

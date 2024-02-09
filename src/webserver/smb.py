from flask import Blueprint, render_template

from src.services.smb_server_alternative import SambaController
bp = Blueprint('smb', __name__, url_prefix='/smb')
from src.helpers.logger import logger
from src.helpers.config import config


@bp.route("/")
def index():
    logger.info("Loading SMB settings...")

    status = SambaController.check_is_running()
    if status is None:
        status_text = "Not running"
    else:
        status_text = "Running"

    status_message = SambaController.get_status_message()

    try:
        username = config.get("smb_service.username")
    except Exception as ex:
        logger.exception(f"Error while loading username: {ex}")
        username = "Unknown"

    try:
        password = config.get("smb_service.password")
    except Exception as ex:
        logger.exception(f"Error while loading password: {ex}")
        password = "Unknown"

    try:
        port = config.get("smb_service.port")
    except Exception as ex:
        logger.exception(f"Error while loading port: {ex}")
        port = "Unknown"

    try:
        share_path = config.get("smb_service.share_path")
    except Exception as ex:
        logger.exception(f"Error while loading share_path: {ex}")
        share_path = "Unknown"

    try:
        return render_template("smb.html",
                               status=status_text,
                               status_message=status_message,
                               username=username,
                               password=password,
                               port=port,
                               share_path=share_path)
    except Exception as e:
        return "Failed loading SMB settings: " + str(e)

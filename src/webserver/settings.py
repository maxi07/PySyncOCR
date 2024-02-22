from flask import Blueprint, render_template, request
bp = Blueprint('settings', __name__, url_prefix='/settings')
from src.helpers.logger import logger
from src.helpers.OpenAI import test_and_add_key
from src.helpers.config import config
from src.helpers.env_manager import update_env_variable
import os


@bp.route("/")
def index():
    logger.info("Loading settings...")
    if "OPEN_AI_KEY" in os.environ:
        logger.debug("OpenAI key found.")
        dummy_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    else:
        logger.debug("OpenAI key not found.")
        dummy_key = ""

    if config.get('web_service.automatic_file_names'):
        logger.debug("Automatic file names enabled.")
        automatic_file_names = True
    else:
        logger.debug("Automatic file names disabled.")
        automatic_file_names = False
    return render_template("settings.html",
                           dummy_key=dummy_key,
                           automatic_file_names=automatic_file_names)


@bp.post("/openai")
def set_openai_key():
    try:
        logger.info("Testing OpenAI key...")
        key = request.form.get("openai_key")
        if key and config.get('web_service.automatic_file_names'):
            logger.debug("Removing OpenAI key...")
            config.set("web_service.automatic_file_names", False)
            update_env_variable("OPEN_AI_KEY", "")
            return {"success": True}, 200
        else:
            res = test_and_add_key(key)
            return {"success": res}, 200 if res else 400
    except Exception as e:
        logger.exception(f"An error occurred while setting OpenAI key: {e}")
        return {"success": False}, 500

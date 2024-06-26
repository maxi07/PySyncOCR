from flask import Blueprint, render_template, request
bp = Blueprint('settings', __name__, url_prefix='/settings')
from src.helpers.logger import logger
from src.helpers.OpenAI import test_and_add_key
from src.helpers.config import config
from src.helpers.env_manager import remove_env_variable
import os


@bp.route("/")
def index():
    logger.info("Loading settings...")
    if "OPEN_AI_KEY" in os.environ:
        logger.debug("OpenAI key found.")
        dummy_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        config.set('web_service.automatic_file_names', True)
    else:
        logger.debug("OpenAI key not found.")
        dummy_key = ""
        config.set('web_service.automatic_file_names', False)

    return render_template("settings.html",
                           dummy_key=dummy_key,
                           automatic_file_names=config.get('web_service.automatic_file_names'))


@bp.post("/openai")
def set_openai_key():
    try:
        key = request.form.get("openai_key")
        if key and config.get('web_service.automatic_file_names'):
            logger.debug("Removing OpenAI key...")
            config.set("web_service.automatic_file_names", False)
            remove_env_variable("OPEN_AI_KEY")
            return {"success": 204}, 200
        else:
            logger.info("Testing OpenAI key...")
            res = test_and_add_key(key)
            if res == 200:
                config.set("web_service.automatic_file_names", True)
            else:
                config.set("web_service.automatic_file_names", False)
            return {"success": res}, 200
    except Exception as e:
        logger.exception(f"An error occurred while setting OpenAI key: {e}")
        return {"success": False}, 500

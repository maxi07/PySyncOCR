from flask import Blueprint, render_template
bp = Blueprint('settings', __name__, url_prefix='/settings')
from src.helpers.logger import logger


@bp.route("/")
def index():
    logger.info("Loading settings...")
    return render_template("settings.html")
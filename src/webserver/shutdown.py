from flask import Blueprint
from src.helpers.logger import logger
bp = Blueprint('shutdown', __name__)
from . import socketio


@bp.route('/shutdown')
def shutdown():
    logger.info("Shutting down...")
    socketio.stop()
    return "Shutting down..."

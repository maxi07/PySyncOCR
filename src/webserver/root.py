import json
from flask import Blueprint, send_file, redirect, url_for
from helpers.logger import logger
from helpers.rclone_management_onedrive import list_remotes
bp = Blueprint('root', __name__)


@bp.route('/')
def index():
    logger.info("Loading index page...")
    return redirect(url_for('dashboard.index'))


@bp.get("/static/images/<path:filename>")
def serve_image(filename):
    logger.info(f"Serving image {filename}")
    image_path = f'static/images/{filename}'

    # Determine mimetype based on file extension
    if filename.lower().endswith('.png'):
        mimetype = 'image/png'
    elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
        mimetype = 'image/jpeg'
    else:
        # Handle other image formats if needed
        mimetype = 'application/octet-stream'

    return send_file(image_path, mimetype=mimetype)

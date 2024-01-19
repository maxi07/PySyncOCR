from flask import Blueprint, jsonify, render_template, request, redirect, g
bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
from src.helpers.logger import logger
from src.webserver.db import get_db

@bp.route("/")
def index():
    try:
        logger.info("Loading dashboard...")
        db = get_db()
        pdfs = db.execute(
            'SELECT * FROM scanneddata '
            'ORDER BY created DESC'
        ).fetchall()
        logger.debug(f"Loaded {len(pdfs)} pdfs")
        return render_template('dashboard.html', pdfs=pdfs)
    except Exception as e:
        logger.exception(e)
        return render_template("dashboard.html", pdfs=[])
    
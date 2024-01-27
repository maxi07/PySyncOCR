from flask import Blueprint, render_template, request, g
bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
from src.helpers.logger import logger
from src.webserver.db import get_db
from src.helpers.config import config
import locale
from datetime import datetime
import math
from . import sock

@bp.route("/")
def index():
    try:
        logger.info("Loading dashboard...")
        db = get_db()
        page = request.args.get('page', 1, type=int)  # Get pageination from url args
        total_entries = db.execute('SELECT COUNT(*) FROM scanneddata').fetchone()[0]
        entries_per_page = 12
        total_pages = math.ceil(total_entries / entries_per_page)
        offset = (page - 1) * entries_per_page
        pdfs = db.execute(
            'SELECT * FROM scanneddata '
            'ORDER BY created DESC '
            'LIMIT :limit OFFSET :offset',
            {'limit': entries_per_page, 'offset': offset}
        ).fetchall()
        logger.debug(f"Loaded {len(pdfs)} pdfs")

        # Set the locale to the user's default
        locale.setlocale(locale.LC_TIME, '')
        logger.debug(f"Locale set to {locale.getlocale()}")

        # Convert sqlite3.Row objects to dictionaries
        pdfs_dicts = [dict(pdf) for pdf in pdfs]

        # Get first use flag
        first_use = bool(config.get("web_service.first_use"))
        config.set("web_service.first_use", False)
        for pdf in pdfs_dicts:
            try:
                input_datetime_created = datetime.strptime(pdf['created'], "%Y-%m-%d %H:%M:%S")
                input_datetime_modified = datetime.strptime(pdf['modified'], "%Y-%m-%d %H:%M:%S")
                pdf['created'] = input_datetime_created.strftime('%d.%m.%Y %H:%M')
                pdf['modified'] = input_datetime_modified.strftime('%d.%m.%Y %H:%M')
            except Exception as ex:
                logger.exception(f"Failed setting datetime for {pdf['id']}. {ex}")
        return render_template('dashboard.html', pdfs=pdfs_dicts, total_pages=total_pages, page=page, first_use=first_use)
    except Exception as e:
        logger.exception(e)
        return render_template("dashboard.html", pdfs=[], total_pages=0, page=1, first_use=False)
    
import json
from flask import Blueprint, render_template, request, current_app
bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
from src.helpers.logger import logger
from src.webserver.db import get_db
from src.helpers.config import config
from src.helpers.time_converter import format_time_difference
import locale
from datetime import datetime
import time
import math
from . import sock
import queue

websocket_messages_queue = queue.Queue()


@bp.route("/")
def index():
    try:
        logger.info("Loading dashboard...")
        db = get_db()
        entries_per_page = 8
        try:
            page = request.args.get('page', 1, type=int)  # Get pageination from url args
            total_entries = db.execute('SELECT COUNT(*) FROM scanneddata').fetchone()[0]
            total_pages = math.ceil(total_entries / entries_per_page)
            offset = (page - 1) * entries_per_page
            pdfs = db.execute(
                'SELECT * FROM scanneddata '
                'ORDER BY created DESC, id DESC '
                'LIMIT :limit OFFSET :offset',
                {'limit': entries_per_page, 'offset': offset}
            ).fetchall()
            logger.debug(f"Loaded {len(pdfs)} pdfs")
        except Exception as e:
            logger.exception(f"Error while loading pdfs: {e}")
            pdfs = []
            total_pages = 1
            page = 1

        # Count total processed PDFs (with status synced)
        try:
            processed_pdfs = db.execute(
                'SELECT COUNT(*) FROM scanneddata '
                'WHERE file_status = "Completed"'
                ).fetchone()[0]
            logger.debug(f"Found {processed_pdfs} processed pdfs")
        except Exception as e:
            logger.exception(f"Error while counting processed pdfs: {e}")
            processed_pdfs = "Unknown"

        # Count total queued PDFs (with status pending)
        try:
            queued_pdfs = db.execute(
                'SELECT COUNT(*) FROM scanneddata '
                'WHERE file_status = "Pending"'
                ).fetchone()[0]
            logger.debug(f"Found {queued_pdfs} queued pdfs")
        except Exception as e:
            logger.exception(f"Error while counting queued pdfs: {e}")
            queued_pdfs = "Unknown"

        # Get the latest timestamp from the file_status=pending
        try:
            latest_timestamp_pending = db.execute(
                'SELECT created FROM scanneddata '
                'WHERE file_status = "Pending" '
                'ORDER BY created DESC '
                'LIMIT 1'
                ).fetchone()
            if latest_timestamp_pending is not None:
                logger.debug(f"Found latest timestamp for pending documents: {latest_timestamp_pending[0]}")
                latest_timestamp_pending_string = "Updated " + format_time_difference(latest_timestamp_pending[0])
            else:
                latest_timestamp_pending_string = "Never"
                logger.debug("No latest timestamp for pending documents found")
        except Exception as e:
            logger.exception(f"Error while getting latest pending timestamp: {e}")
            latest_timestamp_pending_string = "Unknown"

        # Get the latest timestamp from the file_status=completed
        try:
            latest_timestamp_completed = db.execute(
                'SELECT created FROM scanneddata '
                'WHERE file_status = "Completed" '
                'ORDER BY created DESC '
                'LIMIT 1'
                ).fetchone()
            if latest_timestamp_completed is not None:
                logger.debug(f"Found latest timestamp for synced documents: {latest_timestamp_completed[0]}")
                latest_timestamp_completed_string = "Updated " + format_time_difference(latest_timestamp_completed[0])
            else:
                latest_timestamp_completed_string = "Never"
                logger.debug("No latest timestamp for synced documents found")
        except Exception as e:
            logger.exception(f"Error while getting latest synced timestamp: {e}")
            latest_timestamp_completed_string = "Unknown"

        # Set the locale to the user's default
        locale.setlocale(locale.LC_TIME, '')
        logger.debug(f"Locale set to {locale.getlocale()}")

        # Convert sqlite3.Row objects to dictionaries
        pdfs_dicts = list(reversed([dict(pdf) for pdf in pdfs]))

        # Get first use flag
        first_use = bool(config.get("web_service.first_use"))
        if not current_app.debug:
            config.set("web_service.first_use", False)

        if len(pdfs_dicts) > 0:
            for pdf in pdfs_dicts:
                try:
                    input_datetime_created = datetime.strptime(pdf['created'], "%Y-%m-%d %H:%M:%S")
                    input_datetime_modified = datetime.strptime(pdf['modified'], "%Y-%m-%d %H:%M:%S")
                    pdf['created'] = input_datetime_created.strftime('%d.%m.%Y %H:%M')
                    pdf['modified'] = input_datetime_modified.strftime('%d.%m.%Y %H:%M')
                except Exception as ex:
                    logger.exception(f"Failed setting datetime for {pdf['id']}. {ex}")

        return render_template('dashboard.html',
                               pdfs=pdfs_dicts,
                               total_pages=total_pages,
                               page=page,
                               first_use=first_use,
                               entries_per_page=entries_per_page,
                               queued_pdfs=queued_pdfs,
                               processed_pdfs=processed_pdfs,
                               latest_timestamp_completed_string=latest_timestamp_completed_string,
                               latest_timestamp_pending_string=latest_timestamp_pending_string)
    except Exception as e:
        logger.exception(e)
        return render_template("dashboard.html",
                               pdfs=[],
                               total_pages=0,
                               page=1,
                               first_use=False,
                               entries_per_page=12,
                               queued_pdfs="Unknown",
                               processed_pdfs="Unknown",
                               latest_timestamp_pending_string="Unknown",
                               latest_timestamp_completed_string="Unknown")


@sock.route("/websocket")
def websocket_dashboard(ws):
    while True:
        try:
            # Check if there's a message in the queue
            # Then check for the command type (add or update) which will later trigger different js functions
            signal = websocket_messages_queue.get_nowait()  # should be of type int (dbid)
            if "command" in signal:
                logger.debug(f"Got message from websocket queue with command: {signal['command']}")
            else:
                logger.warning(f"Received unexpected message from websocket queue: {signal}")
                continue

            db_id = signal['id']
            db = get_db()
            pdf_list = db.execute(
                'SELECT * FROM scanneddata '
                'WHERE id = :id',
                {'id': db_id}
            ).fetchall()
            pdf = [dict(pdf) for pdf in pdf_list][0]
            logger.debug(f"Loaded {db_id} pdf from db")
            try:
                input_datetime_created = datetime.strptime(pdf['created'], "%Y-%m-%d %H:%M:%S")
                input_datetime_modified = datetime.strptime(pdf['modified'], "%Y-%m-%d %H:%M:%S")
                pdf['created'] = input_datetime_created.strftime('%d.%m.%Y %H:%M')
                pdf['modified'] = input_datetime_modified.strftime('%d.%m.%Y %H:%M')
            except Exception as ex:
                logger.exception(f"Failed setting datetime for {pdf['id']}. {ex}")
            data_to_send = {'id': pdf['id'], 'command': signal['command'], 'data': pdf}
            logger.debug(f"Sending update data for {data_to_send['id']} to websocket")
            ws.send(json.dumps(data_to_send))
        except queue.Empty:
            pass
        time.sleep(0.2)

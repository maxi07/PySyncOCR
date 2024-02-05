from src.helpers.logger import logger
logger.info("Loading ...")
from src.helpers.installer import check_install
import threading
from src.services.watchdog_service import FolderMonitor
from src.services.ocr_service import OcrService
from src.services.sync_service import SyncService
from src.services.flask_service import start_server, start_dev_server
from src.webserver.dashboard import websocket_messages_queue
from src.services.smb_server_alternative import SambaController
from queue import Queue
from src.helpers.config import config
import time
import argparse
import signal
import sys


shutdown_flag = threading.Event()


def shutdown_handler(sig, frame):
    """Signal handler for SIGINT (Ctrl+C)."""
    shutdown_flag.set()
    logger.warning("Shutting down...")


"""
PySyncOCR main module.

This module handles the initialization and running of the various services.
"""

if __name__ == "__main__":
    if not sys.platform.lower().startswith('linux'):
        logger.error("OS is not supported.")
        sys.exit(-1)

    # Register the signal handler for SIGINT
    signal.signal(signal.SIGINT, shutdown_handler)
    logger.info("Starting PySyncOCR...")
    parser = argparse.ArgumentParser(
                    prog='PySyncOCR',
                    description='PySyncOCR is a simple tool to sync scanned PDFs from SMB to cloud and OCR them.')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    parser.add_argument('--smb-port', type=int, help='Port to run the SMB server on')
    args = parser.parse_args()
    if args.dev:
        logger.warning("Running in development mode!")
    check_install()

    root_folder = config.get_filepath("sync_service.root_folder")
    logger.info(f"Root folder is {root_folder}")
    ocr_queue = Queue()
    sync_queue = Queue()

    # Setup SMB

    # This is for the smb_service_old
    # smb_settings = config.get("smb_service")

    # if args.smb_port:
    #     smb_server = MySMBServer(smb_settings, args.smb_port)
    # else:
    #     smb_server = MySMBServer(smb_settings)

    # New SMB setup
    # smb = SambaController()
    # if not smb.check_share_exists(config.get("smb_service.share_name")):
    #     smb.add_share_config(config.get("smb_service.share_name"), config.get_filepath("smb_service.share_path"))
    #     smb.add_user(config.get("smb_service.username"), config.get("smb_service.password"))
    # smb.start_server()

    watchdog = FolderMonitor(root_folder, ocr_queue, websocket_messages_queue)
    ocr_service = OcrService(ocr_queue, sync_queue, websocket_messages_queue)
    sync_service = SyncService(sync_queue, websocket_messages_queue)

    watchdog_thread = threading.Thread(target=watchdog.start_monitoring, name="Watchdog Service")
    ocr_thread = threading.Thread(target=ocr_service.start_processing, name="OCR Service")
    sync_thread = threading.Thread(target=sync_service.start_processing, name="Sync Service")
    # smb_thread = threading.Thread(target=smb_server.start, name="SMB Service")

    if args.dev:
        logger.warning("Running FLASK dev server!")
        flask_thread = threading.Thread(target=start_dev_server, name="Flask Service DEV")
    else:
        flask_thread = threading.Thread(target=start_server, name="Gunicorn Service")

    watchdog_thread.start()
    ocr_thread.start()
    sync_thread.start()
    # smb_thread.start()
    flask_thread.start()

    try:
        while not shutdown_flag.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        # Perform cleanup and shutdown
        shutdown_flag.set()

    watchdog.stop_monitoring()
    watchdog_thread.join()
    logger.debug("Watchdog thread joined")

    # Add a sentinel value to the OCR service's queue to signal it to exit
    ocr_queue.put(None)
    ocr_thread.join()
    logger.debug("OCR thread joined")

    sync_queue.put(None)
    sync_thread.join()
    logger.debug("Sync thread joined")
    flask_thread.join()
    logger.debug("Flask thread joined")
    smb.stop_server()
    # smb_server.stop()
    # smb_thread.is_alive()
    # smb_thread.join()
    logger.info("PySyncOCR stopped. Bye!")

from src.helpers.logger import logger
logger.info("Loading ...")
from src.helpers.installer import check_install
import threading
from src.services.watchdog_service import FolderMonitor
from src.services.ocr_service import OcrService
from src.services.sync_service import SyncService
from src.services.smb_service import MySMBServer
from src.services.flask_service import start_server, start_dev_server
from src.webserver.dashboard import websocket_messages_queue
from queue import Queue
from src.helpers.config import config
import time
import argparse


if __name__ == "__main__":
    logger.info("Starting PySyncOCR...")
    parser = argparse.ArgumentParser(
                    prog='PySyncOCR',
                    description='PySyncOCR is a simple tool to sync scanned PDFs from SMB to cloud and OCR them.')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    args = parser.parse_args()
    if args.dev:
        logger.warning("Running in development mode!")
    check_install()

    root_folder = config.get_filepath("sync_service.root_folder")
    logger.info(f"Root folder is {root_folder}")
    ocr_queue = Queue()
    sync_queue = Queue()

    # Setup SMB
    smb_settings = config.get("smb_service")
    smb_server = MySMBServer(smb_settings)

    watchdog = FolderMonitor(root_folder, ocr_queue, websocket_messages_queue)
    ocr_service = OcrService(ocr_queue, sync_queue, websocket_messages_queue)
    sync_service = SyncService(sync_queue, websocket_messages_queue)

    watchdog_thread = threading.Thread(target=watchdog.start_monitoring, name="Watchdog Service")
    ocr_thread = threading.Thread(target=ocr_service.start_processing, name="OCR Service")
    sync_thread = threading.Thread(target=sync_service.start_processing, name="Sync Service")
    smb_thread = threading.Thread(target=smb_server.start, name="SMB Service")

    if args.dev:
        logger.warning("Running FLASK dev server!")
        flask_thread = threading.Thread(target=start_dev_server, name="Flask Service DEV")
    else:
        flask_thread = threading.Thread(target=start_server, name="Flask Service")

    watchdog_thread.start()
    ocr_thread.start()
    sync_thread.start()
    smb_thread.start()
    flask_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watchdog.stop_monitoring()
        watchdog_thread.join()

        # Add a sentinel value to the OCR service's queue to signal it to exit
        ocr_queue.put(None)
        ocr_thread.join()

        sync_queue.put(None)
        sync_queue.join()
        smb_thread.join()
        flask_thread.join()

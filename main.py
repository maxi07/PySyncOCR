from src.helpers.installer import check_install
import threading
from src.services.watchdog_service import FolderMonitor
from src.services.ocr_service import OcrService
from queue import Queue
from src.helpers.config import config
from src.helpers.logger import logger
import time

if __name__ == "__main__":
    logger.info("Starting PySyncOCR...")
    check_install()

    root_folder = config.get("sync_service.root_folder")
    logger.info(f"Root folder is {root_folder}")
    ocr_queue = Queue()

    watchdog = FolderMonitor(root_folder, ocr_queue)
    ocr_service = OcrService(ocr_queue)

    watchdog_thread = threading.Thread(target=watchdog.start_monitoring, name="Watchdog Service")
    ocr_thread = threading.Thread(target=ocr_service.start_processing, name="OCR Service")

    watchdog_thread.start()
    ocr_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watchdog.stop_monitoring()

        # Add a sentinel value to the OCR service's queue to signal it to exit
        ocr_queue.put(None)
        ocr_thread.join()

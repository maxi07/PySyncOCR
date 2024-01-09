from src.helpers.logger import logger
from queue import Queue
from langdetect import detect
import ocrmypdf
import os
from src.helpers.config import config
from os.path import join
from shutil import copy

def detect_language(text):
    try:
        return detect(text)
    except Exception:
        return 'unknown'

class OcrService:
    def __init__(self, ocr_queue: Queue, sync_queue: Queue):
        self.ocr_queue = ocr_queue
        self.sync_queue = sync_queue

    def start_processing(self):
        logger.info("Started OCR service")
        while True:
            file_path = self.ocr_queue.get()  # Retrieve item from the queue
            if file_path is None:  # Exit command
                break
            logger.info(f"Processing file with OCR: {file_path}")

            try:
                basename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
                dirname = os.path.dirname(file_path)
            except Exception as ex:
                logger.exception(f"Failed extracting file and directory name. {ex}")
                self.ocr_queue.task_done()
                continue

            ocr_file = dirname + "/" + basename_without_ext + "_OCR.pdf"
            try:
                result = ocrmypdf.ocr(file_path, ocr_file, output_type='pdf', skip_text=True, deskew=True, rotate_pages=True, jpg_quality=80, png_quality=80, optimize=2)
                logger.info(f"OCR processing completed: {file_path}")
                logger.debug(f"OCR exited with code {result}")
                logger.debug(f"Adding {ocr_file} to sync queue")
                self.sync_queue.put(ocr_file)

                if config.get("sync_service.keep_original"):
                    try:
                        logger.debug(f"Copying file to original location for backup: {config.get_filepath('sync_service.original')}")
                        copy(file_path, config.get_filepath("sync_service.original"))
                    except Exception as ex:
                        logger.exception("Failed copying to backup location: {ex}")
                else:
                    logger.debug("Skipping file save due to user config.")
            except Exception as ex:
                logger.exception(f"Failed processing {file_path} with OCR: {ex}")
                self.sync_queue.put(file_path)

            self.ocr_queue.task_done()

logger.debug(f"Loaded {__name__} module")

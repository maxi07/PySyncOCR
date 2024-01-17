from src.helpers.logger import logger
from queue import Queue
import ocrmypdf
import PyPDF2
from src.helpers.config import config
from shutil import copy
from src.helpers.ProcessItem import ProcessItem, ProcessStatus, ItemType, OCRStatus
from datetime import datetime

class OcrService:
    def __init__(self, ocr_queue: Queue, sync_queue: Queue):
        self.ocr_queue = ocr_queue
        self.sync_queue = sync_queue

    def start_processing(self):
        logger.info("Started OCR service")
        while True:
            item: ProcessItem = self.ocr_queue.get()
            if item is None:  # Exit command
                break
            item.status = ProcessStatus.OCR
            item.time_ocr_started = datetime.now()

            logger.info(f"Processing file with OCR: {item.local_file_path}")

            # Read PDF file properties
            if item.item_type == ItemType.PDF:
                try:
                    pdf_reader = PyPDF2.PdfReader(item.local_file_path)
                    item.pdf_pages = len(pdf_reader.pages)
                    logger.debug(f"PDF file has {item.pdf_pages} pages to process")
                except Exception as e:
                    logger.error(f"Error reading PDF file: {item.local_file_path}")
                    logger.exception(e)
                    item.time_ocr_finished = datetime.now()
                    item.ocr_status = OCRStatus.FAILED
                    item.status = ProcessStatus.SYNC_PENDING
                    self.sync_queue.put(item)
                    continue
            
            try:
                result = ocrmypdf.ocr(item.local_file_path, item.ocr_file, output_type='pdf', skip_text=True, rotate_pages=True, jpg_quality=80, png_quality=80, optimize=2, language=["eng"])
                logger.info(f"OCR processing completed: {item.local_file_path}")
                logger.debug(f"OCR exited with code {result}")
                logger.debug(f"Adding {item.ocr_file} to sync queue")
                item.ocr_status = OCRStatus.COMPLETED

                if config.get("sync_service.keep_original"):
                    try:
                        logger.debug(f"Copying file to original location for backup: {config.get_filepath('sync_service.original')}")
                        copy(item.local_file_path, config.get_filepath("sync_service.original"))
                    except Exception as ex:
                        logger.exception(f"Failed copying to backup location: {ex}")
                else:
                    logger.debug("Skipping file save due to user config.")
            except ocrmypdf.UnsupportedImageFormatError:
                logger.error(f"Unsupported image format: {item.local_file_path}")
                item.ocr_status = OCRStatus.UNSUPPORTED
            except ocrmypdf.DpiError as dpiex:
                logger.error(f"DPI error: {item.local_file_path} {dpiex}")
                item.ocr_status = OCRStatus.DPI_ERROR
            except ocrmypdf.InputFileError as inex:
                logger.error(f"Input error: {item.local_file_path} {inex}")
                item.ocr_status = OCRStatus.INPUT_ERROR
            except ocrmypdf.OutputFileAccessError as outex:
                logger.error(f"Output error: {item.local_file_path} {outex}")
                item.ocr_status = OCRStatus.OUTPUT_ERROR
            except Exception as ex:
                logger.exception(f"Failed processing {item.local_file_path} with OCR: {ex}")
                item.ocr_status = OCRStatus.FAILED
            finally:
                item.time_ocr_finished = datetime.now()
                item.status = ProcessStatus.SYNC_PENDING
                self.sync_queue.put(item)

            self.ocr_queue.task_done()

logger.debug(f"Loaded {__name__} module")

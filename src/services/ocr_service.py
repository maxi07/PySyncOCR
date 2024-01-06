from src.helpers.logger import logger
from queue import Queue
from langdetect import detect
import ocrmypdf
import os
from multiprocessing import Process
import time


def detect_language(text):
    try:
        return detect(text)
    except Exception:
        return 'unknown'


def ocrmypdf_process(input, output):
    result = ocrmypdf.ocr(input, output, output_type='pdf', skip_text=True, deskew=True, rotate_pages=True, jpg_quality=80, png_quality=80, optimize=2)
    logger.debug(f"ocrmypdf returned with exit code {result}")


def main():
    pdf_input_folder = r"C:\Users\MaximilianKrausePAGE\Downloads"
    file_list = [f for f in os.listdir(path=pdf_input_folder) if f.endswith('.pdf') or f.endswith('.PDF')]
    logger.debug(f"Detected {len(file_list)} PDFs.")

    for file in file_list:
        try:
            logger.info(f"Running OCR on {file}")
            input_filepath = os.path.join(pdf_input_folder, file)
            output_filepath = os.path.join(pdf_input_folder, 'OCR_'+file)
            p = Process(target=ocrmypdf_process, args=(input_filepath, output_filepath))
            p.start()
            p.join()
        except Exception:
            logger.exception(f"Failed running OCR on {file}")
            continue

class OcrService:
    def __init__(self, file_queue: Queue):
        self.file_queue = file_queue

    def start_processing(self):
        logger.info("Started OCR service")
        while True:
            file_path = self.file_queue.get()  # Retrieve item from the queue
            if file_path is None:  # Exit command
                break
            # Add your OCR processing logic here
            logger.info(f"Processing file with OCR: {file_path}")
            # Simulate OCR processing by sleeping for a few seconds
            time.sleep(3)
            logger.info(f"OCR processing completed: {file_path}")
            self.file_queue.task_done()

logger.debug(f"Loaded {__name__} module")

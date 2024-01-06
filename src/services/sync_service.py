from queue import Queue
from src.helpers.logger import logger
import time

class SyncService:
    def __init__(self, file_queue: Queue):
        self.file_queue = file_queue

    def start_processing(self):
        logger.info("Started Sync service.")
        while True:
            file_path = self.file_queue.get()  # Retrieve item from the queue
            if file_path is None:  # Exit command
                break
            # Add your OCR processing logic here
            logger.info(f"Uploading file...: {file_path}")
            # Simulate OCR processing by sleeping for a few seconds
            time.sleep(3)
            logger.info(f"File upload completed: {file_path}")
            self.file_queue.task_done()

logger.debug(f"Loaded {__name__} module")

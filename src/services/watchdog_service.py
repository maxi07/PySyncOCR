import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue
from src.helpers.logger import logger
from src.helpers.config import config
import os
from PIL import Image
from PyPDF2 import PdfReader
from src.helpers.ProcessItem import ItemType, ProcessItem, ProcessStatus

class FileHandler(FileSystemEventHandler):
    """
    Custom file event handler for the watchdog library.

    Attributes:
        file_queue (Queue): A queue to store the paths of newly created files.
    """
    def __init__(self, file_queue: Queue):
        super().__init__()
        self.file_queue = file_queue

    def on_created(self, event):
        """
        Callback method triggered when a file or directory is created.

        Args:
            event (FileSystemEvent): The event object representing the file system event.
        """
        if event.is_directory:
            logger.debug(f"Ignoring new folder at {event.src_path}")
            return
        
        if "_OCR.pdf" in event.src_path:
            logger.debug(f"Ignoring working _OCR file at {event.src_path}")
            return
        
        if ":Zone.Identifier" in event.src_path:
            logger.debug(f"Ignoring Windows Security File file at {event.src_path}")
            try:
                os.remove(event.src_path)
            except OSError:
                pass
            return

        # Ignore files that are hidden and start with a dot based on filename
        basename = os.path.basename(event.src_path)
        if basename.startswith(".") or basename.startswith("_"):
            logger.debug(f"Ignoring hidden file at {event.src_path}")
            return


        if any(substr in event.src_path for substr in [str(config.get("sync_service.failed_dir")), str(config.get("sync_service.original_dir"))]):
            logger.debug(f"Ignoring new file in {event.src_path}")
            return
        
        # Test if file is PDF or image. if neither can be opened, wait five seconds and try again.
        # Repeat this process until a maximum timeout of three minutes is reached
        timeout = 180
        start_time = time.time()

        logger.info(f"Detected new file at {event.src_path}")
        for i in range(timeout):
            if self.is_image(event.src_path):
                item = ProcessItem(event.src_path, ItemType.IMAGE)
                break
            elif self.is_pdf(event.src_path):
                item = ProcessItem(event.src_path, ItemType.PDF)
                break
            else:
                logger.debug(f"Waiting for {event.src_path} for another {int(round(timeout - (time.time() - start_time), 0))} seconds")
                time.sleep(5)
                if time.time() - start_time > timeout:
                    logger.warning(f"File {event.src_path} is neither a PDF or image file. Skipping.")
                    return 

        # Add the new file to the queue
        logger.info(f"Added {item.local_file_path} to OCR queue")
        item.status = ProcessStatus.OCR_PENDING
        self.file_queue.put(item)

    def is_image(self, file_path) -> bool:
        try:
            with Image.open(file_path):
                logger.debug(f"File {file_path} is an image file.")
                return True
        except (IOError, Image.DecompressionBombError):
            return False
        
    def is_pdf(self, file_path):
        try:
            with open(file_path, "rb") as file:
                r = PdfReader(file)
                if len(r.pages) > 0:
                    logger.debug(f"File {file_path} is a PDF file.")
                else:
                    return False
            return True
        except Exception as ex:
            return False


class FolderMonitor:
    """
    Folder monitoring service using the watchdog library and multithreading.

    Attributes:
        root_folder (str): The root folder to monitor.
        file_queue (Queue): A queue for storing file paths.
        event_handler (FileHandler): The custom file event handler.
        observer (Observer): The watchdog observer.
    """
    def __init__(self, root_folder: str, file_queue: Queue):
        self.root_folder = root_folder
        self.file_queue = file_queue
        self.event_handler = FileHandler(self.file_queue)
        self.observer = Observer()

    def start_monitoring(self):
        """
        Start monitoring the specified root folder for file creations.
        Starts the watchdog observer.
        """
        try:
            if not os.path.exists(self.root_folder):
                logger.warning(f"The specified root folder for syncing does not exist: {self.root_folder}")
                logger.info("Creating new sync folder.")
                os.mkdir(self.root_folder)
            self.observer.schedule(self.event_handler, self.root_folder, recursive=True)
            self.observer.start()
        except Exception as e:
            logger.exception("Failed starting watchdog", e)
            return
        logger.info(f"Started watchdog at {self.root_folder}")

    def stop_monitoring(self):
        """
        Stop the monitoring service.
        Stops the watchdog observer.
        """
        self.observer.stop()
        self.observer.join()

        logger.warning("Monitoring service stopped.")

logger.debug(f"Loaded {__name__} module")

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue
from src.helpers.logger import logger
from src.helpers.config import config
import os
from PIL import Image

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

        if any(substr in event.src_path for substr in [str(config.get("sync_service.failed_dir")), str(config.get("sync_service.original_dir"))]):
            logger.debug(f"Ignoring new file in {event.src_path}")
            return
        
        # Test if file is PDF or image
        if not str(event.src_path).lower().endswith(".pdf"):
            # Its not a PDF, test if its an image
            logger.debug("Detected new file, but it doesnt have a PDF extension")
            if not self.is_image(event.src_path):
                logger.debug("File is also not an image - Skipping")
                return
            else:
                logger.debug(f"Detected file as image: {str(event.src_path)}")
        else:
            logger.debug(f"Detected new PDF file: {str(event.src_path)}")
        # Add the new file to the queue
        logger.info(f"Added {event.src_path} to OCR queue")
        self.file_queue.put(event.src_path)

    def is_image(self, file_path) -> bool:
        try:
            with Image.open(file_path):
                return True
        except (IOError, Image.DecompressionBombError):
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

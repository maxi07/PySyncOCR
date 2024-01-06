import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue
from src.config import config
from src.logger import logger

class FileHandler(FileSystemEventHandler):
    """
    Custom file event handler for the watchdog library.

    Attributes:
        file_queue (Queue): A queue to store the paths of newly created files.
    """
    def __init__(self, file_queue):
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
        # Add the new file to the queue
        self.file_queue.put(event.src_path)

class FileHandlerThread(threading.Thread):
    """
    Thread for handling files from the file queue.

    Attributes:
        file_queue (Queue): A queue to retrieve file paths for processing.
    """
    def __init__(self, file_queue):
        super().__init__()
        self.file_queue = file_queue

    def run(self):
        """
        The main method executed when the thread starts.
        Continuously retrieves file paths from the queue and processes them.
        """
        while True:
            file_path = self.file_queue.get()
            if file_path is None:
                break
            # Handle the file here (replace this with your actual file handling logic)
            logger.info(f"Processing file: {file_path}")
            # Simulate file handling by sleeping for a few seconds
            time.sleep(5)
            logger.info(f"File processing completed: {file_path}")
            self.file_queue.task_done()

class FolderMonitor:
    """
    Folder monitoring service using the watchdog library and multithreading.

    Attributes:
        root_folder (str): The root folder to monitor.
        file_queue (Queue): A queue for storing file paths.
        event_handler (FileHandler): The custom file event handler.
        observer (Observer): The watchdog observer.
        file_handler_thread (FileHandlerThread): The thread for handling files from the queue.
    """
    def __init__(self, root_folder):
        self.root_folder = root_folder
        self.file_queue = Queue()
        self.event_handler = FileHandler(self.file_queue)
        self.observer = Observer()
        self.file_handler_thread = FileHandlerThread(self.file_queue)

    def start_monitoring(self):
        """
        Start monitoring the specified root folder for file creations.
        Starts the watchdog observer and the file handling thread.
        """
        try:
            self.observer.schedule(self.event_handler, self.root_folder, recursive=True)
            self.observer.start()
        except OSError as e:
            if e.errno == 2:
                logger.error(f"The specified root folder for syncing does not exist: {self.root_folder}")
                return
        except Exception as e:
            logger.exception("Failed starting watchdog", e)
            return
        logger.info(f"Started watchdog at {self.root_folder}")

        # Start the file handling thread
        self.file_handler_thread.start()

    def stop_monitoring(self):
        """
        Stop the monitoring service.
        Stops the watchdog observer and the file handling thread.
        """
        self.observer.stop()
        self.observer.join()
        
        # Add a sentinel value to the queue to signal the file handler thread to exit
        self.file_queue.put(None)
        self.file_handler_thread.join()

        logger.warning("Monitoring service stopped.")

if __name__ == "__main__":
    root_folder = config.get("sync_service.root_folder")
    
    monitor = FolderMonitor(root_folder)
    monitor.start_monitoring()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()

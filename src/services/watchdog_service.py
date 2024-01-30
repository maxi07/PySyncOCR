import sqlite3
import time
import PyPDF2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue
from src.helpers.logger import logger
from src.helpers.config import config
import os
from PIL import Image
from PyPDF2 import PdfReader
from src.helpers.ProcessItem import ItemType, ProcessItem, ProcessStatus
from src.helpers.rclone_configManager import RcloneConfig
import fitz
from src.webserver.db import update_scanneddata_database


class FileHandler(FileSystemEventHandler):
    """
    Custom file event handler for the watchdog library.

    Attributes:
        file_queue (Queue): A queue to store the paths of newly created files.
    """
    def __init__(self, file_queue: Queue, websocket_messages_queue: Queue):
        super().__init__()
        self.file_queue = file_queue
        self.websocket_messages_queue = websocket_messages_queue

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
        try:
            connection = sqlite3.connect(config.get("sql.db_location"))

            # Create a cursor object
            cursor = connection.cursor()
            cursor.execute(
                'INSERT INTO scanneddata (file_name, local_filepath) '
                'VALUES (?, ?)',
                (item.filename, item.local_directory_above)
            )
            connection.commit()
            last_inserted_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
            connection.close()
            item.db_id = last_inserted_id
        except Exception as e:
            logger.exception(f"Error adding new file to database: {e}")
            last_inserted_id = None

        self.websocket_messages_queue.put({"command": "add", "id": item.db_id})

        try:
            # Generate preview image
            previewimage_path = f'/static/images/pdfpreview/{last_inserted_id}.jpg'
            self.pdf_to_jpeg(item.local_file_path, "src/webserver" + previewimage_path, 128, 50)
            update_scanneddata_database(item.db_id, {'previewimage_path': previewimage_path}, self.websocket_messages_queue)
        except Exception as e:
            logger.exception(f"Error adding preview image to database: {e}")

        try:
            # Matching remote connection
            confitem = RcloneConfig.get(item.local_directory_above)
            if confitem:
                logger.debug(f"Found matching config item: {confitem.id}")
                item.connection = confitem.id
                item.remote_file_path = confitem.remote
                item.remote_directory = confitem.remote.split(":")[1]
                update_scanneddata_database(item.db_id, {'remote_connection_id': item.connection, 'remote_filepath': item.remote_directory}, self.websocket_messages_queue)
            else:
                logger.warning(f"No matching config item found for {item.local_file_path}. Will continue to OCR but uploading will fail.")
        except Exception as e:
            logger.exception(f"Error matching remote connection: {e}")

            # Read PDF file properties
        if item.item_type == ItemType.PDF:
            try:
                pdf_reader = PyPDF2.PdfReader(item.local_file_path)
                item.pdf_pages = len(pdf_reader.pages)
                logger.debug(f"PDF file has {item.pdf_pages} pages to process")
                update_scanneddata_database(item.db_id, {'pdf_pages': item.pdf_pages}, self.websocket_messages_queue)
            except Exception as e:
                logger.error(f"Error reading PDF file: {item.local_file_path}")
                logger.exception(e)
        item.status = ProcessStatus.OCR_PENDING
        logger.info(f"Added {item.local_file_path} to OCR queue")
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
        except Exception:
            return False

    def pdf_to_jpeg(self, pdf_path: str, output_path: str, target_height=128, compression_quality=50):
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Get the first page
        first_page = pdf_document[0]

        # Get the aspect ratio of the page
        aspect_ratio = first_page.rect.width / first_page.rect.height

        # Calculate the corresponding width based on the target height
        target_width = int(target_height * aspect_ratio)

        # Create a matrix for the desired size
        matrix = fitz.Matrix(target_width / first_page.rect.width, target_height / first_page.rect.height)

        # Create a pixmap for the page with the specified size
        pixmap = first_page.get_pixmap(matrix=matrix)

        # Save the pixmap as a JPEG image with compression
        pixmap.save(output_path, "jpeg", jpg_quality=compression_quality)

        # Close the PDF document
        pdf_document.close()


class FolderMonitor:
    """
    Folder monitoring service using the watchdog library and multithreading.

    Attributes:
        root_folder (str): The root folder to monitor.
        file_queue (Queue): A queue for storing file paths.
        event_handler (FileHandler): The custom file event handler.
        observer (Observer): The watchdog observer.
    """
    def __init__(self, root_folder: str, file_queue: Queue, websocket_messages_queue: Queue):
        self.root_folder = root_folder
        self.file_queue = file_queue
        self.event_handler = FileHandler(self.file_queue, websocket_messages_queue)
        self.observer = Observer()
        self.websocket_messages_queue = websocket_messages_queue

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

        logger.info("Monitoring service stopped.")


logger.debug(f"Loaded {__name__} module")

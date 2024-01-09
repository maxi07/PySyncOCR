from queue import Queue
from src.helpers.logger import logger
from src.helpers.rclone_configManager import RcloneConfig
from src.helpers.config import config
from src.helpers.rclone_management_onedrive import upload_file
import os
from shutil import move
from os.path import join, expanduser

class SyncService:
    def __init__(self, file_queue: Queue):
        self.file_queue = file_queue

    def start_processing(self):
        logger.info("Started Sync service")
        while True:
            file_path = self.file_queue.get()  # Retrieve item from the queue

            try:
                if file_path is None:  # Exit command
                    break
                
                logger.info(f"Received new item for upload: {file_path}")
                # Test for local filepath
                subdirname = os.path.basename(os.path.dirname(file_path))
                logger.debug(f"Extracted subdirname: {subdirname}")
                filename = os.path.basename(file_path)
                logger.debug(f"Extracted filename: {filename}")
                confitem = RcloneConfig.get(subdirname)
                if confitem is None:
                    logger.error(f"Cannot sync {file_path} as no matching onedrive config was found.")
                else:
                    logger.debug(f"Found matching config item: {confitem.id}")
                    logger.info(f"Uploading file...: {file_path}")
                    res = upload_file(file_path, join(confitem.remote, filename.replace("_OCR", "")))  # Remove the "_OCR" from the filepath
                    if res == False:
                        self.move_to_failed(file_path)
                    else:
                        logger.debug("Removing original file")
                        os.remove(file_path.replace("_OCR", ""))
            except Exception as ex:
                logger.exception(f"Failed syncing {file_path}: {ex}")
                self.move_to_failed(file_path)
            finally:
                self.file_queue.task_done()

    def move_to_failed(self, file_path: str):
        try:
            failed_dir = config.get_filepath('sync_service.failed_dir')
            if not os.path.exists(failed_dir):
                os.mkdir(failed_dir)
            logger.debug(f"Moving file {file_path} to failed directory at {join(failed_dir, os.path.basename(file_path))}")
            move(file_path, join(failed_dir, os.path.basename(file_path)))
        except Exception as ex:
            logger.exception(f"Failed moving item from {file_path} to {str(config.get_filepath('sync_service.failed_dir'))}")

logger.debug(f"Loaded {__name__} module")

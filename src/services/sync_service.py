from queue import Queue
from src.helpers.logger import logger
from src.helpers.rclone_configManager import RcloneConfig
from src.helpers.config import config
from src.helpers.rclone_management_onedrive import upload_file
import os
from shutil import move
from os.path import join
from src.helpers.ProcessItem import ProcessItem, ProcessStatus
from datetime import datetime
from src.webserver.db import update_scanneddata_database

class SyncService:
    def __init__(self, file_queue: Queue):
        self.file_queue = file_queue

    def start_processing(self):
        logger.info("Started Sync service")
        while True:
            item: ProcessItem = self.file_queue.get()  # Retrieve item from the queue
            if item is None:  # Exit command
                break
            item.status = ProcessStatus.SYNC
            item.time_upload_started = datetime.now()

            update_scanneddata_database(item.db_id, {"file_status": item.status.value})

            try:             
                logger.info(f"Received new item for upload: {item.ocr_file}")
                confitem = RcloneConfig.get(item.local_directory_above)
                if confitem is None:
                    logger.error(f"Cannot sync {item.ocr_file} as no matching onedrive config was found.")
                    item.status = ProcessStatus.SYNC_FAILED
                    self.move_to_failed(item.ocr_file)
                    if os.path.exists(item.local_file_path.replace("_OCR", "")):
                        logger.debug(f"Removing original file at {item.local_file_path.replace('_OCR', '')}")
                        os.remove(item.local_file_path.replace("_OCR", ""))
                else:
                    logger.debug(f"Found matching config item: {confitem.id}")
                    logger.info(f"Uploading file...: {item.ocr_file}")
                    res = upload_file(item.ocr_file, join(confitem.remote, item.filename.replace("_OCR", "")))  # Remove the "_OCR" from the filepath
                    if res == False:
                        item.status = ProcessStatus.SYNC_FAILED
                        self.move_to_failed(item.local_file_path)
                    else:
                        item.status = ProcessStatus.COMPLETED
                        if os.path.exists(item.local_file_path.replace("_OCR", "")):
                            logger.debug(f"Removing original file at {item.local_file_path.replace('_OCR', '')}")
                            os.remove(item.local_file_path.replace("_OCR", ""))
            except Exception as ex:
                logger.exception(f"Failed syncing {item.local_file_path}: {ex}")
                item.status = ProcessStatus.SYNC_FAILED
                self.move_to_failed(item.local_file_path)
            finally:
                item.time_finished = datetime.now()
                update_scanneddata_database(item.db_id, {"file_status": item.status.value})
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

from src.helpers.ProcessItem import OCRStatus, ProcessItem, ItemType
from src.services.ocr_service import OcrService
import queue
import pytest
from shutil import copytree, rmtree
from src.helpers.logger import logger
import os


class OCRServiceTest:
    def __init__(self):
        self.ocr_queue = queue.Queue()
        self.sync_queue = queue.Queue()
        self.websocket_messages_queue = queue.Queue()
        self.ocr_service = OcrService(self.ocr_queue, self.sync_queue, self.websocket_messages_queue)


@pytest.fixture
def setup_ocr_service():
    # Copy assets dir for restore later
    try:
        copytree("tests/assets", "tests/assets_backup", dirs_exist_ok=True)
    except Exception as ex:
        logger.exception(f"Failed to copy assets for testing: {ex}")
        raise ex

    # Create a new OCR service
    try:
        ocr_service = OCRServiceTest()
        yield ocr_service
    finally:
        # Cleanup
        rmtree("tests/assets")
        copytree("tests/assets_backup", "tests/assets")
        rmtree("tests/assets_backup")


@pytest.mark.filterwarnings("ignore:pikepdf is missing some specialized decoders")
def test_general(setup_ocr_service):
    ocr_service = setup_ocr_service.ocr_service
    # Now test the start_processing and put something into the queue
    item = ProcessItem("tests/assets/cardinal.pdf", ItemType.PDF)
    ocr_service.ocr_queue.put(item)
    ocr_service.ocr_queue.put(None)  # Quit the loop
    ocr_service.start_processing()
    assert item.ocr_status == OCRStatus.COMPLETED
    assert item.ocr_file == "tests/assets/cardinal_OCR.pdf"
    assert os.path.isfile(item.ocr_file)
    assert item.time_ocr_started is not None
    assert item.time_ocr_finished is not None
    assert ocr_service.sync_queue.get() == item

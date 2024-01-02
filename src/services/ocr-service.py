import pytesseract
import platform
from src.logger import logger
from langdetect import detect
import ocrmypdf
import os
from multiprocessing import Process


def detect_language(text):
    try:
        return detect(text)
    except Exception:
        return 'unknown'


def ocrmypdf_process(input, output):
    result = ocrmypdf.ocr(input, output, output_type='pdf', skip_text=True, deskew=True, rotate_pages=True, jpg_quality=80, png_quality=80, optimize=2)
    logger.debug(f"ocrmypdf returned with exit code {result}")


def main():
    if platform.system() == 'Windows':
        logger.debug("Detected Windows plattform, setting path to tesseract.")
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    logger.debug(f"Running tesseract version {pytesseract.get_tesseract_version()}")
    logger.debug(f"Available languages: {pytesseract.get_languages()}")

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


if __name__ == "__main__":
    main()

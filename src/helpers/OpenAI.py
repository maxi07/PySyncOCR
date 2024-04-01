from openai import OpenAI, AuthenticationError, RateLimitError
from src.helpers.env_manager import update_env_variable
from src.helpers.logger import logger
from src.helpers.config import config
import os
from pypdf import PdfReader
from src.webserver.dashboard import websocket_messages_queue


def test_and_add_key(key) -> int:
    """
    Tests if an OpenAI API key is valid, adds it to the environment if so,
    and returns a status code indicating whether it was valid.

    Parameters:
    - key (str): The OpenAI API key to test.

    Returns:
    - int: 200 if valid, 401 if invalid, 400 on other exception.
    """
    client = OpenAI(
        api_key=key,
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Please respond with the words 'it works'"}
            ]
        )
        if completion.choices[0].message.content == "it works":
            logger.info("OppenAI key is valid")
            update_env_variable("OPEN_AI_KEY", key)
            return 200
        else:
            logger.warning("OpenAI key worked, but did not return 'it works'")
            return 200
    except AuthenticationError:
        logger.warning("OpenAI key is invalid")
        return 401
    except RateLimitError:
        logger.warning("OPENAI rate limit reached! Either not enough credits or too many requests.")
        return 429
    except Exception as e:
        logger.exception(f"An error occurred while testing OpenAI key: {e}")
        return 400


def generate_filename(pdf_path: str) -> str:
    """
    Generates a filename for a PDF based on its content using OpenAI.

    Tries to extract the text from the PDF. If OpenAI is configured, sends the text to OpenAI to generate a filename.
    Otherwise, just returns the original filename.

    Parameters:
    - pdf_path (str): The path to the PDF file.

    Returns:
    - str: The generated filename if successful, otherwise the original filename.
    """
    logger.debug(f"Generating filename for {pdf_path}")
    # Get filename
    try:
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
    except Exception as ex:
        logger.exception(f"Failed getting filename: {ex}")
        return "unknown"

    if not config.get("web_service.automatic_file_names"):
        logger.warning("Automatic files names are disabled")
        return filename

    if "OPEN_AI_KEY" not in os.environ:
        logger.warning("OpenAI key was not found")
        return filename

    # Get PDF Text
    pdf_text = extract_text(pdf_path)

    client = OpenAI(
        api_key=os.environ["OPEN_AI_KEY"],
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Identify a suitable filename for the following pdf content. Keep the language of the file name in the original language and do not add any other language. Avoid special characters. Do not add a file extension. Seperate words with a underscore. Have a maximum filename length of 50 characters."},
                {"role": "user", "content": pdf_text}
            ]
        )
        openai_filename = completion.choices[0].message.content
        if openai_filename:
            logger.debug(f"Received OpenAI filename: {openai_filename}")
            return openai_filename
        else:
            logger.warning("OpenAI key worked, but did not return any result.")
            return filename
    except AuthenticationError:
        logger.warning("OpenAI key is invalid")
        websocket_messages_queue.put({"command": "toast", "style": "warning", "message": "Cannot generate file name: OpenAI Key is invalid."})
        return filename
    except RateLimitError:
        logger.warning("OpenAI rate limit reached! Either not enough credits or too many requests.")
        websocket_messages_queue.put({"command": "toast", "style": "warning", "message": "Cannot generate file name: OpenAI Key is invalid."})
        return filename
    except Exception as e:
        logger.exception(f"An error occurred while testing OpenAI key: {e}")
        websocket_messages_queue.put({"command": "toast", "style": "warning", "message": f"Cannot generate file name: {e}"})
        return filename


def extract_text(pdf_path: str) -> str:
    """Extracts text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF. An empty string is returned if the extraction fails.
    """
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        text = page.extract_text()
        return text
    except Exception as ex:
        logger.exception(f"Failed extracting text: {ex}")
        return ""

from openai import OpenAI
from src.helpers.env_manager import update_env_variable
from src.helpers.logger import logger


def test_and_add_key(key) -> bool:
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
            return True
        else:
            logger.warning("OpenAI key worked, but did not return 'it works'")
            return True
    except Exception as e:
        logger.exception(f"An error occurred while testing OpenAI key: {e}")
        return False

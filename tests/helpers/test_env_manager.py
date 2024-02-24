from src.helpers.env_manager import update_env_variable, remove_env_variable
import os


def test_envmanager():
    try:
        update_env_variable("API_KEY", "new_api_key_value", env_file_path='.env-test')
        assert os.environ['API_KEY'] == 'new_api_key_value'

        update_env_variable("API_KEY", "new_api_key_value_2", env_file_path='.env-test')
        assert os.environ['API_KEY'] == 'new_api_key_value_2'

        update_env_variable("API_KEY2", "new_api_key_value_3", env_file_path='.env-test')
        assert os.environ['API_KEY2'] == 'new_api_key_value_3'

        remove_env_variable("API_KEY", env_file_path='.env-test')
        remove_env_variable("API_KEY2", env_file_path='.env-test')
        assert 'API_KEY' not in os.environ
        assert 'API_KEY2' not in os.environ
    finally:
        os.remove('.env-test')

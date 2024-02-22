import os
from src.helpers.logger import logger


def update_env_variable(key, value, env_file_path='.env') -> bool:
    updated_lines = []

    try:
        # Read the existing .env file
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as env_file:
                lines = env_file.readlines()
        else:
            logger.debug(f"Environment file '{env_file_path}' not found.")
            logger.debug(f"Creating environment file '{env_file_path}'.")
            lines = []                

        # Update the value of the specified key
        key_found = False
        for line in lines:
            if line.startswith(f'{key}='):
                updated_lines.append(f'{key}={value}\n')
                key_found = True
            else:
                updated_lines.append(line)

        # If the key wasn't found, add it to the end of the file
        if not key_found:
            updated_lines.append(f'{key}={value}\n')

        # Write the updated lines back to the .env file
        with open(env_file_path, 'w') as env_file:
            env_file.writelines(updated_lines)

        # Load the updated .env file into the environment
        os.environ[key] = value

        logger.debug(f"Environment variable '{key}' updated with value '{value}'.")
        return True
    except Exception as e:
        logger.exception(f"An error occurred while updating environment variable '{key}': {e}")
        return False

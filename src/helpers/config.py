import json
from typing import Any
from src.helpers.logger import logger
from os.path import expanduser, join


class Config:
    def __init__(self, config_file):
        self._config_file = config_file
        try:
            with open(config_file) as f:
                self._config = json.load(f)
                logger.debug("Reading config")
        except Exception as ex:
            logger.exception(f"Failed reading config: {ex}")
            quit(-2)

    def __iter__(self):
        return iter(self._config.items())

    def __len__(self):
        return len(self._config)

    def get(self, key: str, default=None):
        try:
            keys = key.split('.')
            value = self._config
            for k in keys:
                value = value.get(k, {})
            # logger.debug(f"Read config key {key} with value {value} of type {type(value)}")
            return value if value is not None else default
        except Exception as ex:
            logger.exception(f"Failed reading config: {ex}")
            return default

    def get_filepath(self, key: str, default=None):
        try:
            keys = key.split('.')
            value = self._config
            for k in keys:
                value = value.get(k, {})
            logger.debug(f"Read config key {key} with value {value} of type {type(value)}")
            if value is not None:
                return join(expanduser('~'), value)
            else:
                return default
        except Exception as ex:
            logger.exception(f"Failed reading config: {ex}")
            return default

    def set(self, key, value):
        try:
            keys = key.split('.')
            curr_dict = self._config
            for k in keys[:-1]:
                curr_dict = curr_dict.setdefault(k, {})
            curr_dict[keys[-1]] = value
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f)
            logger.debug(f"Set config key '{key}' with value '{value}'")
        except Exception as ex:
            logger.exception(f"Failed saving {key} setting to config", ex)

    def __getattr__(self, name: str) -> Any:
        # Allow auto-completion for existing keys
        if name in self.settings:
            return self.get(name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


config = Config('src/configs/config.json')
logger.debug(f"Loaded {__name__} module")

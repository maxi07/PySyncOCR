import logging
import coloredlogs


# Set up the logger
logger = logging.getLogger(__name__)
"""Example usage
```python
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```"""

# Set the logging level
logger.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Create a colored formatter
colored_formatter = coloredlogs.ColoredFormatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level_styles={
        'debug': {'color': 'white'},
        'info': {'color': 'white'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'red'},
    }
)

# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(colored_formatter)

# Create a file handler and set the formatter
file_handler = logging.FileHandler("logfile.log")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


logger.debug(f"Loaded {__name__} module")

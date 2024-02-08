import logging
import coloredlogs


# Set up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a colored formatter
colored_formatter = coloredlogs.ColoredFormatter(
    "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
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
file_handler.setFormatter(colored_formatter)

# Add both handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# Customize log messages before formatting
def custom_emit(self, record):
    try:
        message = self.format(record)
        if 'DEBUG' in message:
            message = message.replace('DEBUG', '\033[35mDEBUG\033[0m')  # Pink color for DEBUG
        if 'INFO' in message:
            message = message.replace('INFO', '\033[32mINFO\033[0m')    # Green color for INFO
        if 'WARNING' in message:
            message = message.replace('WARNING', '\033[33mWARNING\033[0m')  # Yellow color for WARNING
        if 'ERROR' in message:
            message = message.replace('ERROR', '\033[31mERROR\033[0m')    # Red color for ERROR
        self.stream.write(message + self.terminator)
        self.flush()
    except Exception:
        self.handleError(record)


console_handler.emit = custom_emit.__get__(console_handler, logging.StreamHandler)

logger.debug(f"Loaded {__name__} module")

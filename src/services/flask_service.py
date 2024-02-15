from src.webserver import create_app
from src.helpers.logger import logger
from src.webserver import socketio

gunicorn_process = None  # Global variable to hold the gunicorn process
stop_server_flag = False  # Flag to indicate when to stop the server


def stop_server():
    """Function to stop the gunicorn server."""
    global gunicorn_process, stop_server_flag
    if gunicorn_process and not stop_server_flag:
        gunicorn_process.terminate()
        stop_server_flag = True


def start_socketio_server():
    logger.info("Starting socketio server...")
    app = create_app()
    socketio.run(app, debug=False, allow_unsafe_werkzeug=False, log_output=True, use_reloader=False)


def start_dev_server():
    app = create_app()
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    app.run(debug=True, use_reloader=False, threaded=True)
    app.errorhandler(Exception)(lambda e: logger.exception(e))

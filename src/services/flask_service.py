from src.webserver import create_app
from src.helpers.logger import logger
import subprocess
import os

gunicorn_process = None  # Global variable to hold the gunicorn process
stop_server_flag = False  # Flag to indicate when to stop the server


def stop_server():
    """Function to stop the gunicorn server."""
    global gunicorn_process, stop_server_flag
    if gunicorn_process and not stop_server_flag:
        gunicorn_process.terminate()
        stop_server_flag = True


def start_server():
    global gunicorn_process, stop_server_flag
    python_interpreter = os.path.join(os.getcwd(), '.venv', 'bin', 'python')

    gunicorn_command = [
        python_interpreter,
        '-m', 'gunicorn',
        '-w', '4',  # Number of worker processes
        '-b', '0.0.0.0:5000',  # Host and port on which to bind
        'src.webserver:create_app()',  # Replace with your actual app module and instance
    ]

    try:
        gunicorn_process = subprocess.Popen(gunicorn_command)
        gunicorn_process.wait()  # Wait for the process to finish
    except Exception as e:
        logger.error(f"Error running Gunicorn: {e}")
    finally:
        # Perform cleanup before exiting
        logger.info("Gunicorn server stopped.")


def start_dev_server():
    app = create_app()
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    app.run(debug=True, use_reloader=False, threaded=True)

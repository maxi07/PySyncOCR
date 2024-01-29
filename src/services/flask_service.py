from src.webserver import create_app
from src.helpers.logger import logger
import subprocess
def start_server():
    gunicorn_command = [
        'gunicorn',
        '-w', '4',  # Number of worker processes
        '-b', '0.0.0.0:5000',  # Host and port on which to bind
        'src.webserver:create_app()',  # Replace with your actual app module and instance
    ]

    try:
        subprocess.run(gunicorn_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Gunicorn: {e}")

def start_dev_server():
    app = create_app()
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    app.run(debug=True, use_reloader=False, threaded=True)
###### DO NOT USE ######

from flask import Flask, render_template, request
from src.helpers.logger import logger
from src.helpers.rclone_management_onedrive import dump_config, delete_config_item

app = Flask(__name__, template_folder='../webserver/templates')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/settings')
def settings():
    try:
        logger.info("Loading settings...")
        onedrive_configs = dump_config()
        return render_template('settings.html', onedrive_configs=onedrive_configs, test="test")
    except Exception as e:
        logger.exception(e)
        return render_template('settings.html', onedrive_configs=[])




            

def run_flask():
    app.run(debug=True)
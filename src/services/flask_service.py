from flask import Flask
from src.helpers.logger import logger

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!' 

def run_flask():
    app.run(debug=True, use_reloader=False)
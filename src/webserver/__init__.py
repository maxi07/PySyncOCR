import os
from flask_sock import Sock
from flask import Flask
from helpers.logger import logger
from webserver.context_processor import inject_template_data
from . import root

sock = Sock()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'pysyncocr.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize websocket
    sock.init_app(app)

    # initialize SQL db
    from . import db
    db.init_app(app)

    from . import dashboard
    from . import sync
    app.register_blueprint(root.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(sync.bp)
    app.template_context_processors[None].append(inject_template_data)
    logger.debug(f"Registered blueprints with routes {app.url_map}")
    logger.info("Started FLASK server")
    return app

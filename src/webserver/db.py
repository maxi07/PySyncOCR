import sqlite3
import click
from flask import current_app, g
from src.helpers.logger import logger
from functools import wraps

def get_db():
    logger.info("Creating database connection")
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    logger.info("Closing database connection")
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    logger.info("Initializing database")

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def with_database(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Connect to the database
        connection = sqlite3.connect('instance/pysyncocr.sqlite')
        cursor = connection.cursor()

        # Call the wrapped function with the cursor as a keyword argument
        kwargs['cursor'] = cursor

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            # Handle exceptions if needed
            connection.rollback()
            raise e
        finally:
            # Commit the changes and close the connection
            connection.commit()
            connection.close()

        return result

    return wrapper

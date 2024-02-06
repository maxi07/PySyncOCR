import sqlite3
import click
from flask import current_app, g
from helpers.logger import logger
from helpers.config import config


def get_db():
    # logger.debug("Creating database connection")
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    # logger.debug("Closing database connection")
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


def update_scanneddata_database(id: int, update_values: dict, websocketQueue=None):
    """Updates the scanned data database table with new values for the given ID.

    Connects to the SQLite database, constructs a dynamic SQL query to update
    the row with the given ID and the provided update_values dictionary.
    Commits the changes and closes the connection. Also optionally enqueues
    an "update" command for the updated ID to a websocket queue.

    Handles any errors and logs exceptions.
    """
    try:
        # Connect to the database
        connection = sqlite3.connect(config.get("sql.db_location"))

        # Create a cursor object
        cursor = connection.cursor()
        logger.debug(f"Received values: {update_values} with keys {update_values.keys()} to update SQL db for id {id}")

        # Construct the SET part of the query dynamically based on the dictionary
        set_clause = ', '.join(f'{key} = ?' for key in update_values.keys())

        # Update the scanneddata table
        query = f'UPDATE {config.get("sql.db_pdf_table")} SET {set_clause}, modified = CURRENT_TIMESTAMP WHERE id = ?'
        cursor.execute(query, (*update_values.values(), id))
        logger.debug(f"Updated database {config.get('sql.db_location')} for id {id} with values {update_values}")

        # Commit the changes and close the connection
        connection.commit()
        connection.close()

        if websocketQueue is None:
            logger.warning("Websocket queue is None, did we forget to pass it to the function?")
        else:
            logger.debug(f"Updated websocket queue with update command for id {id}")
            websocketQueue.put({"command": "update", "id": id})
    except Exception as ex:
        logger.exception(f"Error updating database for id {id}: {ex}")


def send_database_request(query: str):
    """Sends a request to the database and returns the result.

    Connects to the SQLite database, executes the provided query,
    and returns the result.
    Commits the changes and closes the connection.

    Handles any errors and logs exceptions.
    """
    try:
        # Connect to the database
        connection = sqlite3.connect(config.get("sql.db_location"))

        # Create a cursor object
        cursor = connection.cursor()

        # Execute the query
        logger.debug("Sending database request: " + query)
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchall()

        # Commit the changes and close the connection
        connection.commit()
        connection.close()

        return result
    except Exception as ex:
        logger.exception(f"Error sending database request: {ex}")

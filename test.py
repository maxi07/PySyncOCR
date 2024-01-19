import sqlite3

# Connect to the database
connection = sqlite3.connect('instance/pysyncocr.sqlite')

# Create a cursor object
cursor = connection.cursor()

cursor.execute('UPDATE scanneddata SET file_status = ?, modified = CURRENT_TIMESTAMP WHERE id = ?', ("Test", 8))

# Commit the changes and close the connection
connection.commit()
connection.close()

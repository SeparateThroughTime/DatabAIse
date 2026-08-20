"""Module to create a database where databases are saved for analysis.

This is not primary to the software. If no database.db exists, the software
will run fine. But after terminating all created databases will be lost
without it.

To create a clean database.db file run this file once before starting DatabAIse.
Then all databases will be stored inside it.
"""

import sqlite3
import traceback

con = sqlite3.connect("databases.db")
cur = con.cursor()

try:
    cur.execute("CREATE TABLE databases(database_id integer PRIMARY KEY, topic varchar(255), sql_file text(65535));")
except sqlite3.OperationalError:
    print("Database already exists! If you want a new database, delete the old before.")
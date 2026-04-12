import sqlite3

con = sqlite3.connect("databases.db")
cur = con.cursor()

# Only run once on server to create Database, that is collecting the sql files, that are created with the tool
cur.execute("CREATE TABLE databases(database_id integer PRIMARY KEY, topic varchar(255), sql_file text(65535));")
#print(cur.execute("SELECT * FROM databases").fetchall())
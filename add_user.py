import os
import sqlite3

db_filename = 'Chat-server.db'
schema_filename = 'create_schema.sql'
db_is_new = not os.path.exists(db_filename)

with sqlite3.connect(db_filename) as conn:
    if db_is_new:
        with open(schema_filename, 'rt') as f:
            schema = f.read()
        conn.executescript(schema)
    else:
        pass
    username = input("Enter the username: ")
    password = input("Enter the password: ")
    if username != '' and password != '':
        conn.execute("""
            insert into credentials (username,password)
            values (?, ?)
            """, (username, password))

    pass

import sqlite3

connection = sqlite3.connect('parts.db')
cursor = connection.cursor()
cursor.execute(
    'CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, description TEXT,'
    ' created_at DATETIME, updated_at DATETIME)'
)
connection.commit()
connection.close()

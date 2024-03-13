import sqlite3
from src.model import Part


class PartsRepository:
    def __init__(self):
        self.collection = sqlite3.connect('parts.db')
        self.collection.execute(
            'CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, description TEXT)'
        )

    async def create(self, part: Part) -> int:
        cursor = self.collection.cursor()
        cursor.execute(
            'INSERT INTO parts (name, quantity, description) VALUES (?, ?, ?)',
            (part.name, part.quantity, part.description),
        )
        self.collection.commit()
        return cursor.lastrowid

    async def get(self, part_number: int) -> Part:
        cursor = self.collection.cursor()
        cursor.execute('SELECT * FROM parts WHERE id = ?', (part_number,))
        return cursor.fetchone()

    async def list(self) -> list:
        cursor = self.collection.cursor()
        cursor.execute('SELECT * FROM parts')
        return cursor.fetchall()

import sqlite3
from src.model import Part


class PartsRepository:
    def __init__(self):
        self.collection = sqlite3.connect('parts.db')
        self.collection.execute(
            'CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, description TEXT)'
        )

    def _execute(self, query: str, parameters: tuple = ()) -> list:
        return self.collection.cursor().execute(query, parameters)

    async def create(self, part: Part) -> int:
        cursor = self._execute(
            query='INSERT INTO parts (name, quantity, description) VALUES (?, ?, ?)',
            parameters=(part.name, part.quantity, part.description),
        )
        self.collection.commit()
        return cursor.lastrowid

    async def get(self, part_number: int) -> Part:
        return self._execute(query='SELECT * FROM parts WHERE id = ?', parameters=(part_number,)).fetchone()

    async def list(self) -> list:
        return self._execute('SELECT * FROM parts').fetchall()

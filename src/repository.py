from datetime import datetime, timezone
import sqlite3
from src.model import Part


class PartsRepository:
    def __init__(self):
        self.collection = sqlite3.connect('parts.db')
        self.collection.execute(
            'CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, description TEXT,'
            ' created_at DATETIME, updated_at DATETIME)'
        )

    def _execute(self, query: str, parameters: tuple = ()) -> list:
        return self.collection.cursor().execute(query, parameters)

    def _set_date(self, part: Part) -> Part:
        part.created_at = str(datetime.now(timezone.utc))
        part.updated_at = str(datetime.now(timezone.utc))

    async def create(self, part: Part) -> int:
        self._set_date(part)
        cursor = self._execute(
            query='INSERT INTO parts (name, quantity, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
            parameters=(
                part.name,
                part.quantity,
                part.description,
                part.created_at,
                part.updated_at,
            ),
        )
        self.collection.commit()
        return cursor.lastrowid

    async def get(self, part_number: int) -> Part:
        return self._execute(query='SELECT * FROM parts WHERE id = ?', parameters=(part_number,)).fetchone()

    async def list(self) -> list:
        return self._execute('SELECT * FROM parts').fetchall()

    async def update(self, part_number: int, part: Part) -> None:
        part.updated_at = str(datetime.now(timezone.utc))
        self._execute(
            query='UPDATE parts SET name = ?, quantity = ?, description = ?, updated_at = ? WHERE id = ?',
            parameters=(
                part.name,
                part.quantity,
                part.description,
                part.updated_at,
                part_number,
            ),
        )
        self.collection.commit()

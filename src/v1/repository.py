from datetime import datetime, timezone
import sqlite3
from src.v1.model import Part


class PartsRepository:
    def __init__(self):
        self.collection = sqlite3.connect('parts.db')
        self.collection.execute(
            'CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, description TEXT,'
            ' created_at DATETIME, updated_at DATETIME)'
        )

    def _execute(self, query: str, parameters: tuple = ()) -> list:
        return self.collection.cursor().execute(query, parameters)

    def _set_date(self, part: Part) -> None:
        part.created_at = str(datetime.now(timezone.utc))
        part.updated_at = part.created_at

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

    async def update(self, part_number: int, data_to_update: dict) -> None:
        update_queries = []
        update_parameters = []

        if 'name' in data_to_update:
            update_queries.append('name = ?')
            update_parameters.append(data_to_update['name'])

        if 'quantity' in data_to_update:
            update_queries.append('quantity = ?')
            update_parameters.append(data_to_update['quantity'])

        if 'description' in data_to_update:
            update_queries.append('description = ?')
            update_parameters.append(data_to_update['description'])

        update_queries.append('updated_at = ?')
        update_parameters.append(str(datetime.now(timezone.utc)))

        update_query = 'UPDATE parts SET {} WHERE id = ?'.format(', '.join(update_queries))
        update_parameters.append(part_number)

        self._execute(query=update_query, parameters=tuple(update_parameters))
        self.collection.commit()

    async def delete(self, part_number: int) -> None:
        self._execute(query='DELETE FROM parts WHERE id = ?', parameters=(part_number,))
        self.collection.commit()

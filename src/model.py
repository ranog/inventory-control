from pydantic import BaseModel


class Part(BaseModel):
    name: str
    quantity: int
    description: str
    created_at: str = None
    updated_at: str = None

from pydantic import BaseModel


class Part(BaseModel):
    name: str
    quantity: int
    description: str

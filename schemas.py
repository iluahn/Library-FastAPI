from pydantic import BaseModel, Field
from typing import Optional

class Book(BaseModel):
    name: str = Field(min_length=2)
    description: Optional[str] = None

class User(BaseModel):
    name: str = Field(min_length=2)
    email: str = Field(min_length=2)
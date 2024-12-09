# app/models/link.py

from pydantic import BaseModel

class Link(BaseModel):
    rel: str  # e.g., 'self', 'next', 'prev'
    href: str

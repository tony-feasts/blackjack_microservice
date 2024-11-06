# app/models/pagination.py

from pydantic import BaseModel
from typing import Any, List
from app.models.link import Link

class Page(BaseModel):
    data: List[Any]
    links: List[Link]

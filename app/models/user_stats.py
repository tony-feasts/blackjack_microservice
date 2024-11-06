# app/models/user_stats.py

from pydantic import BaseModel
from typing import Optional, List
from app.models.link import Link

class UserStats(BaseModel):
    username: Optional[str] = None
    wins: Optional[int]
    losses: Optional[int]
    links: Optional[List[Link]] = None

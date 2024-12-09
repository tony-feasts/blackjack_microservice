# app/models/game_history.py

from pydantic import BaseModel
from typing import Optional, List
from app.models.result_enum import ResultEnum
from app.models.link import Link

class GameHistory(BaseModel):
    game_id: Optional[int] = None
    username: str
    result: ResultEnum
    links: Optional[List[Link]] = None

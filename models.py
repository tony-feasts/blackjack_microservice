# models.py

from pydantic import BaseModel
from enum import Enum
from typing import Optional, List

# Enum for possible game results
class ResultEnum(str, Enum):
    win = "win"
    loss = "loss"
    push = "push"

# Model for hypermedia links
class Link(BaseModel):
    rel: str    # Relationship type (e.g., 'self', 'next', 'prev')
    href: str   # Hyperlink reference

# Model for GameHistory records
class GameHistory(BaseModel):
    game_id: Optional[int] = None          # Unique ID of the game
    username: str                   # Username of the player
    result: ResultEnum              # Result of the game
    links: List[Link] = []  # Hypermedia links

# Model for UserStats records
class UserStats(BaseModel):
    username: str                   # Username of the player
    wins: int                       # Total number of wins
    losses: int                     # Total number of losses
    links: List[Link] = []  # Hypermedia links

# app/models/name_change.py

from pydantic import BaseModel

class UsernameChangeRequest(BaseModel):
    old_username: str
    new_username: str
    callback_url: str

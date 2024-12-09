# routers/user_stats.py

from fastapi import APIRouter, HTTPException, Request
from old.botched_sprint2.models import UserStats
from old.botched_sprint2.database import execute_query

router = APIRouter()

@router.get("/user_stats/{username}", response_model=UserStats, name='get_user_stats')
def get_user_stats(username: str, request: Request):
    """
    Retrieve user statistics by username.
    Includes self link.
    """
    query = "SELECT * FROM user_stats WHERE username = %s"
    result = execute_query(query, (username,), fetchone=True)

    if result:
        result['links'] = [
            {"rel": "self", "href": str(request.url_for('get_user_stats', username=username))},
            {"rel": "game_history", "href": f"/game_history/?username={username}"}
        ]
        return result
    else:
        raise HTTPException(status_code=404, detail="User not found")

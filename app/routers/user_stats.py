# app/routers/user_stats.py

from fastapi import (APIRouter, HTTPException, Request, Response, status,
                     BackgroundTasks)
from app.resources import UserStatsResource
from app.models import UserStats, Link
from app.models.name_change import UsernameChangeRequest
from asyncio import sleep
import httpx
router = APIRouter()
user_stats_resource = UserStatsResource()

@router.get("/user_stats/{username}", response_model=UserStats)
def get_user_stats(username: str, request: Request):
    result = user_stats_resource.get_by_key(username)
    if result:
        result.links = [
            Link(rel="self", href=str(request.url)),
            Link(rel="game_history",
                 href=f"/game_history/?username={username}")
        ]
        return result
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/user_stats/", status_code=status.HTTP_202_ACCEPTED)
def create_user_stats(user_stats: UserStats,
                      request: Request, response: Response,
                      background_tasks: BackgroundTasks):
    existing_user = user_stats_resource.get_by_key(user_stats.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    async def process_user_creation():
        await sleep(10)
        user_stats.wins = 0
        user_stats.losses = 0
        user_stats_resource.create(user_stats)

    background_tasks.add_task(process_user_creation)
    location_url = request.url_for("get_user_stats",
                                   username=user_stats.username)
    response.headers["Location"] = str(location_url)
    return {"message": "User stats creation started; "
                       "check back later for completion."}

@router.put("/user_stats/{username}")
def update_user_stats(username: str, user_stats: UserStats):
    result = user_stats_resource.update(username, user_stats)
    if result:
        return {"message": "User stats updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/user_stats/{username}")
def delete_user_stats(username: str):
    result = user_stats_resource.delete(username)
    if result:
        return {"message": "User stats deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/user_stats/")
def change_username(user_name_change_request: UsernameChangeRequest,
                    background_tasks: BackgroundTasks):
    old_username = user_name_change_request.old_username
    new_username = user_name_change_request.new_username
    callback_url = user_name_change_request.callback_url
    existing_user = user_stats_resource.get_by_key(old_username)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_stats_resource.get_by_key(new_username):
        raise HTTPException(status_code=400, detail="Username already taken")

    async def process_username_change():
        await sleep(10)
        user_stats_resource.change_username(old_username, new_username)
        callback_data = {"message": "Username changed successfully",
                         "old_username": old_username,
                         "new_username": new_username}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(callback_url,
                                             json=callback_data, timeout=5.0)
                response.raise_for_status()
        except httpx.RequestError as e:
            print(f"Request failed or timed out: {e}")

    background_tasks.add_task(process_username_change)
    return {"message": "Username change initiated; "
                       "client will be notified upon completion."}

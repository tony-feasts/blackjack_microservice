# app/main.py

from fastapi import FastAPI
from framework.middleware.logging_middleware import LoggingMiddleware
from app.routers import game_history, user_stats

app = FastAPI()

app.add_middleware(LoggingMiddleware)

app.include_router(game_history.router)
app.include_router(user_stats.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

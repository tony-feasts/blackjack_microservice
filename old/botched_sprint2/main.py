# main.py

from fastapi import FastAPI
from old.botched_sprint2.middleware import LoggingMiddleware
from old.botched_sprint2.routers import user_stats, game_history
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(game_history.router)
app.include_router(user_stats.router)

# Error handling
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import HTTPException

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

# Application entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

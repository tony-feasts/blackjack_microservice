from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

# Database connection configuration
db_config = {
    'user': 'admin',
    'password': 'pass',  # Replace with your actual MySQL root password
    'host': 'cloudproject.crimg8c22499.us-east-2.rds.amazonaws.com',
    'database': 'blackjack',
}

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Endpoint to get wins and losses by username
@app.get("/get_scores/")
def get_scores(username: str = Query(...)):
    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query the database for the user's scores
        query = "SELECT wins, losses FROM records WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            wins, losses = result
            return {"username": username, "wins": wins, "losses": losses}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        cursor.close()
        conn.close()

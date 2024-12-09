# database.py

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'dbuserdbuser')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'blackjack')

def get_db_connection():
    """
    Establishes a connection to the MySQL database.

    Returns:
        mysql.connector.connection_cext.CMySQLConnection: Database connection object.
    """
    return mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME
    )

def execute_query(query: str, params: tuple = (), fetchone=False, fetchall=False):
    """
    Executes a SQL query with optional parameters.

    Args:
        query (str): The SQL query to execute.
        params (tuple): Parameters to pass to the query.
        fetchone (bool): If True, fetches one record.
        fetchall (bool): If True, fetches all records.

    Returns:
        The result of the query execution or None.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None
        return result
    finally:
        cursor.close()
        conn.close()

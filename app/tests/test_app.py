import pytest
import pymysql

@pytest.fixture
def conn():
    """Fixture to connect to the existing MySQL database."""
    # Replace these credentials with your MySQL database connection details
    connection = pymysql.connect(
        host='localhost',  # Replace with your MySQL server's hostname
        user='root',       # Replace with your MySQL username
        password='dbuserdbuser',  # Replace with your MySQL password
        database='blackjack',  # Replace with your database name
        autocommit=True
    )
    yield connection
    connection.close()

def test_user_stats_vs_game_history(conn):
    """Test that user_stats table correctly reflects wins in game_history."""
    cursor = conn.cursor()

    # Query to count wins from game_history for each user
    cursor.execute("""
    SELECT username, COUNT(*) as win_count
    FROM game_history
    WHERE result = 'win'
    GROUP BY username
    """)
    game_history_wins = cursor.fetchall()

    # Debugging output to verify data fetched from game_history
    print("Game history wins:", game_history_wins)

    # Query to get wins from user_stats
    cursor.execute("SELECT username, wins FROM user_stats")
    user_stats = {row[0]: row[1] for row in cursor.fetchall()}

    # Debugging output to verify data fetched from user_stats
    print("User stats:", user_stats)

    # Assert that wins match between game_history and user_stats
    for username, win_count in game_history_wins:
        assert username in user_stats, f"User {username} not found in user_stats"
        assert user_stats[username] == win_count, f"Mismatch for user {username}"

    print("All tests passed! The wins in user_stats match game_history.")

if __name__ == "__main__":
    # Manual execution
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='dbuserdbuser',
        database='user',
        autocommit=True
    )
    try:
        test_user_stats_vs_game_history(connection)
    finally:
        connection.close()

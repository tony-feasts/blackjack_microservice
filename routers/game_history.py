# routers/game_history.py

from fastapi import APIRouter, HTTPException, Response, Query, Request
from typing import List, Optional, Dict, Any
from models import GameHistory, ResultEnum, Link
from database import execute_query

router = APIRouter()

@router.get("/game_history/", response_model=Dict[str, Any], name='get_game_histories')
def get_game_histories(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    result: Optional[ResultEnum] = Query(None),
    username: Optional[str] = Query(None)
):
    """
    Retrieve game histories with pagination and optional filtering.
    Includes self, prev, and next links for pagination.
    Each entry includes a self link and user_stats link (if username is provided).
    """
    # Build the base query
    query = "SELECT * FROM game_history"
    filters = []
    params = []

    if result:
        filters.append("result = %s")
        params.append(result.value)
    if username:
        filters.append("username = %s")
        params.append(username)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Get total records for pagination
    count_query = query.replace("SELECT *", "SELECT COUNT(*) AS total")
    total_records = execute_query(count_query, tuple(params), fetchone=True)
    total = total_records['total'] if total_records else 0

    # Add ordering and pagination to the query
    query += " ORDER BY game_id DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    # Execute the query
    results = execute_query(query, tuple(params), fetchall=True)
    if results is None:
        results = []

    # Build data with links
    data = []
    for record in results:
        game_id = record['game_id']
        record_links = [
            {"rel": "self", "href": str(request.url_for('get_game_history', game_id=game_id))}
        ]
        if 'username' in record:
            record_links.append({"rel": "user_stats", "href": str(request.url_for('get_user_stats', username=record['username']))})
        record['links'] = record_links
        data.append(record)

    # Build pagination links
    base_url = str(request.url).split('?')[0]
    query_params = dict(request.query_params)
    links = [{"rel": "self", "href": str(request.url)}]

    # Next link
    if skip + limit < total:
        next_skip = skip + limit
        next_params = query_params.copy()
        next_params['skip'] = str(next_skip)
        next_params['limit'] = str(limit)
        next_query = "&".join([f"{k}={v}" for k, v in next_params.items()])
        links.append({"rel": "next", "href": f"{base_url}?{next_query}"})

    # Prev link
    if skip > 0:
        prev_skip = max(skip - limit, 0)
        prev_params = query_params.copy()
        prev_params['skip'] = str(prev_skip)
        prev_params['limit'] = str(limit)
        prev_query = "&".join([f"{k}={v}" for k, v in prev_params.items()])
        links.append({"rel": "prev", "href": f"{base_url}?{prev_query}"})

    # Include user_stats link if username is specified
    if username:
        links.append({"rel": "user_stats", "href": str(request.url_for('get_user_stats', username=username))})

    # Construct the final response
    response = {
        "data": data,
        "links": links
    }

    return response

@router.post("/game_history/", response_model=GameHistory, status_code=201)
def create_game_history(game: GameHistory, response: Response, request: Request):
    """
    Create a new game history record and update user statistics.
    """
    # Insert into game_history
    insert_game_query = """
        INSERT INTO game_history (username, result)
        VALUES (%s, %s)
    """
    execute_query(insert_game_query, (game.username, game.result.value))

    # Get the last inserted game_id
    game_id_query = "SELECT LAST_INSERT_ID() AS game_id"
    result = execute_query(game_id_query, fetchone=True)
    game.game_id = result['game_id']

    # Update user_stats
    select_user_query = "SELECT wins, losses FROM user_stats WHERE username = %s"
    user_stats = execute_query(select_user_query, (game.username,), fetchone=True)

    if user_stats:
        wins = user_stats['wins']
        losses = user_stats['losses']
        if game.result == ResultEnum.win:
            wins += 1
        elif game.result == ResultEnum.loss:
            losses += 1

        update_user_query = "UPDATE user_stats SET wins = %s, losses = %s WHERE username = %s"
        execute_query(update_user_query, (wins, losses, game.username))
    else:
        wins = 1 if game.result == ResultEnum.win else 0
        losses = 1 if game.result == ResultEnum.loss else 0
        insert_user_query = "INSERT INTO user_stats (username, wins, losses) VALUES (%s, %s, %s)"
        execute_query(insert_user_query, (game.username, wins, losses))

    # Set the Location header
    location = str(request.url_for('get_game_history', game_id=game.game_id))
    response.headers["Location"] = location

    # Add links to the response
    game.links = [
        {"rel": "self", "href": location},
        {"rel": "user_stats", "href": str(request.url_for('get_user_stats', username=game.username))}
    ]

    return game

@router.get("/game_history/{game_id}", response_model=GameHistory, name='get_game_history')
def get_game_history(game_id: int, request: Request):
    """
    Retrieve a specific game history record by game_id.
    Includes self and user_stats links.
    """
    query = "SELECT * FROM game_history WHERE game_id = %s"
    result = execute_query(query, (game_id,), fetchone=True)

    if result:
        result['links'] = [
            {"rel": "self", "href": str(request.url_for('get_game_history', game_id=game_id))},
            {"rel": "user_stats", "href": str(request.url_for('get_user_stats', username=result['username']))}
        ]
        return result
    else:
        raise HTTPException(status_code=404, detail="Game history not found")

@router.put("/game_history/{game_id}", response_model=GameHistory)
def update_game_history(game_id: int, game: GameHistory, request: Request):
    """
    Update a specific game history record and adjust user statistics accordingly.
    """
    # Check if the game exists
    select_query = "SELECT * FROM game_history WHERE game_id = %s"
    existing_game = execute_query(select_query, (game_id,), fetchone=True)

    if not existing_game:
        raise HTTPException(status_code=404, detail="Game history not found")

    old_result = existing_game['result']
    new_result = game.result.value

    if old_result != new_result:
        # Update user_stats
        select_user_query = "SELECT wins, losses FROM user_stats WHERE username = %s"
        user_stats = execute_query(select_user_query, (game.username,), fetchone=True)

        if user_stats:
            wins = user_stats['wins']
            losses = user_stats['losses']

            # Adjust counts
            if old_result == 'win':
                wins -= 1
            elif old_result == 'loss':
                losses -= 1

            if new_result == 'win':
                wins += 1
            elif new_result == 'loss':
                losses += 1

            # Update or delete user_stats
            if wins == 0 and losses == 0:
                # Remove user_stats entry if no wins or losses remain
                delete_user_stats_query = "DELETE FROM user_stats WHERE username = %s"
                execute_query(delete_user_stats_query, (game.username,))
            else:
                update_user_query = "UPDATE user_stats SET wins = %s, losses = %s WHERE username = %s"
                execute_query(update_user_query, (wins, losses, game.username))
        else:
            pass  # Should not happen since user_stats should exist

    # Update the game record
    update_query = "UPDATE game_history SET result = %s WHERE game_id = %s"
    execute_query(update_query, (new_result, game_id))

    # Return the updated game record with links
    updated_game = get_game_history(game_id, request)
    return updated_game

@router.delete("/game_history/{game_id}", status_code=204)
def delete_game_history(game_id: int):
    """
    Delete a specific game history record and adjust user statistics accordingly.
    """
    # Check if the game exists
    select_query = "SELECT * FROM game_history WHERE game_id = %s"
    existing_game = execute_query(select_query, (game_id,), fetchone=True)

    if not existing_game:
        raise HTTPException(status_code=404, detail="Game history not found")

    username = existing_game['username']
    result = existing_game['result']

    # Delete the game record
    delete_query = "DELETE FROM game_history WHERE game_id = %s"
    execute_query(delete_query, (game_id,))

    # Update user_stats
    select_user_query = "SELECT wins, losses FROM user_stats WHERE username = %s"
    user_stats = execute_query(select_user_query, (username,), fetchone=True)

    if user_stats:
        wins = user_stats['wins']
        losses = user_stats['losses']

        # Adjust counts
        if result == 'win':
            wins -= 1
        elif result == 'loss':
            losses -= 1

        # Check if there are any more game history records for the user
        count_query = "SELECT COUNT(*) AS count FROM game_history WHERE username = %s"
        count_result = execute_query(count_query, (username,), fetchone=True)
        game_count = count_result['count']

        if game_count == 0:
            # Remove user_stats since no more games exist for the user
            delete_user_stats_query = "DELETE FROM user_stats WHERE username = %s"
            execute_query(delete_user_stats_query, (username,))
        else:
            # Update user_stats
            update_user_query = "UPDATE user_stats SET wins = %s, losses = %s WHERE username = %s"
            execute_query(update_user_query, (wins, losses, username))

    return Response(status_code=204)

@router.delete("/game_history/user/{username}", status_code=204)
def delete_user_game_history(username: str):
    """
    Delete all game history records and user statistics for a specific user.
    """
    # Delete all game history records for the user
    delete_game_history_query = "DELETE FROM game_history WHERE username = %s"
    execute_query(delete_game_history_query, (username,))

    # Delete user_stats entry
    delete_user_stats_query = "DELETE FROM user_stats WHERE username = %s"
    execute_query(delete_user_stats_query, (username,))

    return Response(status_code=204)

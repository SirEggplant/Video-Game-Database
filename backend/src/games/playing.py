"""Game purchase, rating, and play session tracking."""
import psycopg # pyright: ignore[reportMissingImports]
import random
from src.db import execute_query


def buy_game(user_id: str, parts: list):
    """Purchase a game (add to owned games with a random initial rating)."""
    game_title = " ".join(parts[1:])
    rating = random.randint(1, 5) # noqa

    if not user_id or not game_title:
        return None

    sql_insert = """
        INSERT INTO user_owns_game (user_uuid, game_uuid, rating)
        VALUES (%s, %s, %s)
        RETURNING game_uuid
    """
    try:
        game_id = get_game_from_title(game_title)
        if not game_id:
            return None
        execute_query(sql_insert, (user_id, game_id, rating))
        return game_title
    except Exception:
        return None


def rate_game(user_id: str, parts: list):
    """Update the rating of a game the user owns."""
    if len(parts) < 2 or not parts[-1].isdigit():
        return None

    game_title = " ".join(parts[1:-1])
    rating = int(parts[-1])

    if not user_id or not game_title:
        return None

    rating = max(1, min(5, rating))

    sql_update = """
        UPDATE user_owns_game
        SET rating = %s
        WHERE game_uuid = %s AND user_uuid = %s
    """
    try:
        game_id = get_game_from_title(game_title)
        if not game_id:
            return None
        execute_query(sql_update, (rating, game_id, user_id))
        return (game_title, rating)
    except Exception:
        return None


def play_game(user_id: str, parts: list):
    """Record a play session for a game or a random game from a collection."""
    collection_name = ""
    game_title = ""
    time_played = 0

    if len(parts) > 1 and parts[1].isdigit():
        # play <minutes> <game title>
        time_played = int(parts[1])
        game_title = " ".join(parts[2:])
    elif len(parts) > 1 and parts[-1].isdigit():
        # play <collection name> <minutes>
        time_played = int(parts[-1])
        collection_name = " ".join(parts[1:-1])
    elif len(parts) > 1:
        # play <game title>  → random duration
        game_title = " ".join(parts[1:])
        time_played = random.randint(1, 120) # noqa

    if not user_id or time_played <= 0:
        return None

    if collection_name:
        game_id = get_random_game_from_collection(collection_name, user_id)
        if not game_id:
            return None
        game_title = collection_name
    else:
        game_id = get_game_from_title(game_title)
        if not game_id:
            return None

    sql_check_owned = """
        SELECT game_uuid FROM user_owns_game
        WHERE game_uuid = %s AND user_uuid = %s
    """
    sql_insert_play = """
        INSERT INTO user_plays (game_uuid, user_uuid, time_played)
        VALUES (%s, %s, %s)
        RETURNING game_uuid
    """
    sql_update_user = """
        UPDATE "user"
        SET total_playtime = total_playtime + %s
        WHERE user_uuid = %s
    """
    try:
        owned = execute_query(sql_check_owned, (game_id, user_id), fetchone=True)
        if not owned:
            return None
        execute_query(sql_insert_play, (game_id, user_id, time_played))
        execute_query(sql_update_user, (time_played, user_id))
        return (game_title, time_played)
    except Exception:
        return None


def get_game_from_title(game_title: str):
    """Return a game UUID by partial title match, or None if not found."""
    if not game_title:
        return None
    sql = """
        SELECT game_uuid FROM game_listing
        WHERE title ILIKE %s
        LIMIT 1
    """
    try:
        result = execute_query(sql, (f"%{game_title}%",), fetchone=True)
        return str(result[0]) if result else None
    except Exception:
        return None


def get_random_game_from_collection(collection_name: str, user_id: str):
    """Return a random game UUID from a user's collection."""
    if not collection_name or not user_id:
        return None

    sql = """
        SELECT cc.game_uuid
        FROM collection_contains cc
        JOIN collection c ON c.collection_uuid = cc.collection_uuid
        WHERE c.collection_name = %s AND c.user_uuid = %s
    """
    try:
        rows = execute_query(sql, (collection_name, user_id), fetchall=True)
        if not rows:
            return None
        return str(random.choice(rows)[0]) # noqa
    except Exception:
        return None
    
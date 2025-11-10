import psycopg # pyright: ignore[reportMissingImports]
import uuid
import random
from db_Connection import execute_query


def buy_Game(user_id: str, parts):
    
    game_title = " ".join(parts[1:])
    rating = random.randint(1,5)

    if not user_id or not game_title:
        return None
    
    sql_insert = """
        INSERT INTO user_owns_game
        (user_uuid, game_uuid, rating)
        VALUES (%s, %s, %s)
        RETURNING game_uuid
    """

    try:
        # Add wildcards for partial matching
        game_id = get_game_from_title(game_title)
        execute_query(sql_insert, (user_id, game_id, rating))
        # Return game_id string as useful success indicator
        return game_title
    except:
        # Optionally log the exception e here
        return None


def rate_Game(user_id: str, parts):

    if len(parts) >= 2 and parts[-1].isdigit():
        game_title = " ".join(parts[1:-1])
        rating = int(parts[-1])
    else:
        return None

    try:
        if not rating:
            return None
        elif rating > 5:
            rating = 5
        elif rating < 1:
            rating = 1
    except:
        if not user_id or not game_title:
            return None

    sql_update = """
        UPDATE user_owns_game 
        SET rating = %s 
        WHERE game_UUID = %s and user_UUID = %s
    """

    try:
        game_id = get_game_from_title(game_title)

        execute_query(sql_update, (rating, game_id, user_id))
        return (game_title, rating)
    except:
        return None


def play_Game(user_id: str, parts):

    if len(parts) > 1 and parts[1].isdigit():
        game_title = " ".join(parts[2:])  # safe to use if length >=3; else this will be empty string
        time_played = int(parts[1])
    elif len(parts) > 0 and parts[-1].isdigit():
        time_played = int(parts[-1])
        collection_name = " ".join(parts[1:-1])  # empty if length < 3
        game_title = ""
    else:
        game_title = " ".join(parts[1:])
        time_played = str(random.randint(1, 120))

        
    if game_title == "":
            game_id = get_Random_Game_From_Collection(collection_name, user_id)

    sql_select_game = """
        SELECT user_owns_game.game_UUID 
        FROM user_owns_game
        WHERE game_uuid = %s AND user_UUID = %s """

    try:
        game_id = get_game_from_title(game_title)
        owned = execute_query(sql_select_game, (game_id,user_id), fetchone=True)
        if not owned:
            return None
    except:
        if not user_id or not time_played:
            return None

    sql_update = """
            UPDATE "user" 
            SET total_playtime = total_playtime + %s
            WHERE user_uuid = %s
        """

    sql_insert = """
        INSERT INTO user_plays
        (game_UUID, user_UUID, time_played)
        VALUES(%s, %s, %s)
        RETURNING game_UUID
    """

    try:
        execute_query(sql_insert,(game_id, user_id, time_played))
        execute_query(sql_update, (time_played, user_id))
        return (game_title, time_played)
    except:
        return None
    
def get_game_from_title(game_title: str):
    sql_select = """
        SELECT game_uuid
        FROM game_listing
        WHERE title ILIKE %s
    """
    
    try:
        pattern = f"%{game_title}%"
        game_id_result = execute_query(sql_select, (pattern,), fetchone=True)
        game_id_str = str(game_id_result[0])
        if game_id_str == "":
            return None
        return game_id_str
    except:
        None
    
def get_Random_Game_From_Collection(collection_name: str, user_id: str):
    if not collection_id and not user_id:
        return None

    
    sql_select_collection = """
        SELECT collection_UUID 
        FROM collection
        WHERE collection_name = %s and user_UUID = %s
    """

    sql_select_game = """
        SELECT game_UUID FROM collection
        WHERE collection_UUID = %s and user_UUID = %s
    """
    try:
        collection_id = execute_query(sql_select_collection, (collection_name, user_id), fetchone=True)
        collection_id = collection_id["collection_UUID"]

        result = execute_query(sql_select_game, (collection_id, user_id), fetchone=True)
        if not result or not result.get("collection"):
            return None
        
        game_list = result["collection"]
        if not game_list:
            return None
        
        index = random.randint(0, len(game_list) - 1)
        return game_list[index]
    except:
        return None
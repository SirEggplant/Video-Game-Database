import psycopg # pyright: ignore[reportMissingImports]
import uuid
import random
from db_Connection import execute_query


def buy_Game(user_id: str, parts):
    
    game_title = " ".join(parts[1:])
    rating = None

    if not user_id or not game_title:
        return None
    
    sql_select = """
        SELECT game_UUID
        FROM game
        WHERE title ILIKE %s
    """
    
    sql_insert = """
        INSERT INTO user_owns_game
        (user_UUID, game_UUID, time_played)
        VALUES(%s, %s, %s::esrb)
        RETURNING game_UUID
    """

    try:
        game_id = execute_query(sql_select, (game_title,), fetchone=True)
        if not game_id or not game_id.get("game_UUID"):
            return None
        
        execute_query(sql_insert, (user_id, str(game_id.get("game_UUID")), rating))
    except:
        return None

def rate_Game(user_id: str, parts):

    if len(parts) >= 2 and parts[1].isdigit():
        game_title = parts[2:]
        rating = int(parts[1])
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

    sql_select = """
        SELECT game_UUID
        FROM game
        WHERE title = %s
    """

    sql_update = """
        UPDATE user_owns_game 
        SET rating = %s 
        WHERE game_UUID = %s and user_UUID = %s
    """

    try:
        game_id = execute_query(sql_select, (game_title), fetchone=True)
        if not game_id or not game_id.get("game_UUID"):
            return None

        execute_query(sql_update, (rating, game_id, user_id))
    except:
        return None


def play_Game(user_id: str, parts):

    if len(parts) == 2 and parts[1].isdigit():
        game_title = parts[2:]
        time_played = int(parts[1])
    elif len(parts) == 2 and parts[:1].isdigit():
        time_played = int(parts[1:])
        collection_name = parts[:1]
    else:
        game_title = " ".join(parts[1:])
        time_played = random.randint(1, 120)

    sql_select_game = """
        SELECT user_owns_game.game_UUID 
        FROM user_owns_game
        INNER JOIN game on user_owns_game.game_UUID = game.game_UUID
        WHERE title ILIKE %s AND user_owns_game.user_UUID = %s """

    try:
        print(game_title)
        print(user_id)
        game_id = execute_query(sql_select_game, (game_title, str(user_id)), fetchone=True)
        print(game_id)
        if not game_id or not game_id.get("game_UUID"):
            return None
        
        if time_played == 0:
            time_played = random.randint(1,120)

        if game_id == "":
            game_id = get_Random_Game_From_Collection(collection_name, user_id)
    except:
        if not user_id or not time_played or (not game_id):
            return None

    sql_update = """
        UPDATE game_listing 
        SET total_playtime_minutes = total_playtime_minutes + %s 
        WHERE game_UUID = %s
    """

    sql_insert = """
        INSERT INTO user_plays
        (game_UUID, user_UUID, time_played)
        VALUES(%s, %s, %s)
        RETURNING game_UUID
    """

    try:
        execute_query(sql_insert,(game_id, user_id, time_played))
        execute_query(sql_update, (time_played, game_id))
        return game_id
    except:
        return None
    
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
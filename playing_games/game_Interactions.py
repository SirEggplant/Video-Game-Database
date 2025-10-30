import psycopg # pyright: ignore[reportMissingImports]
import uuid
import random
from SteamUltraDeluxHDRemixRemastered2.connection import connect_to_db, execute_query


def buy_Game(user_id: str, game_title: str, rating=None):
    
    if not user_id or not game_title:
        return None
    
    sql_select = """
        SELECT game_uuid
        FROM game_listing
        WHERE game_title = %s
    """
    
    sql_insert = """
        INSERT INTO user_owns_game
        (user_uuid, game_uuid, time_played)
        VALUES(%s, %s, %s::esrb)
        RETURNING game_uuid
    """

    try:
        game_id = execute_query(sql_select, (game_title), fetchone=True)
        if not game_id or not game_id.get("game_uuid"):
            return None
        
        execute_query(sql_insert, (user_id, game_id, rating))
    except:
        return None

def rate_Game(user_id: str, game_title: str, rating: int):
    
    try:
        if rating > 5:
            rating = 5
        elif rating < 1:
            rating = 1
    except:
        if not user_id or not game_title or not rating:
            return None

    sql_select = """
        SELECT game_uuid
        FROM game_listing
        WHERE game_title = %s
    """

    sql_update = """
        UPDATE user_owns_game 
        SET rating = %s 
        WHERE game_uuid = %s and user_uuid = %s
    """

    try:
        game_id = execute_query(sql_select, (game_title), fetchone=True)
        if not game_id or not game_id.get("game_uuid"):
            return None

        execute_query(sql_update, (rating, game_id, user_id))
    except:
        return None


def play_Game(user_id: str, game_title: str, time_played: int, collection_name: str):

    sql_select_game = """
        SELECT game_uuid, user_uuid, total_playtime_minutes 
        FROM game_listing and collection
        WHERE user_uuid = %s AND game_uuid = %s
    """

    try:
        game_id = execute_query(sql_select_game, (game_title), fetchone=True)
        if not game_id or not game_id.get("game_uuid"):
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
        SET total_playtime_minutes = %s 
        WHERE game_uuid = %s
    """

    sql_insert = """
        INSERT INTO user_plays
        (game_uuid, user_uuid, time_played)
        VALUES(%s, %s, %s::esrb)
        RETURNING game_uuid
    """

    try:
        execute_query(sql_insert,(game_id, user_id, time_played))

        execute_query(sql_update, (time_played, game_id))
    except:
        return None
    
def get_Random_Game_From_Collection(collection_name: str, user_id: str):
    if not collection_id and not user_id:
        return None

    
    sql_select_collection = """
        SELECT collection_uuid 
        FROM collection
        WHERE collection_name = %s and user_uuid = %s
    """

    sql_select_game = """
        SELECT game_uuid FROM collection
        WHERE collection_uuid = %s and user_uuid = %s
    """
    try:
        collection_id = execute_query(sql_select_collection, (collection_name, user_id), fetchone=True)
        collection_id = collection_id["collection_uuid"]

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
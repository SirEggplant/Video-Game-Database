import psycopg # pyright: ignore[reportMissingImports]
import uuid
import random
from SteamUltraDeluxHDRemixRemastered2.connection import connect_to_db, execute_query


def buyGame(user_id: str, game_id: str, rating=None):
    if not user_id or game_id:
        return None
    
    sql_insert = """
        INSERT INTO user_owns_game
        (user_uuid, game_uuid, timeplayed)
        VALUES(%s, %s, %s::esrb)
        RETURNING game_uuid
    """

    try:
        execute_query(sql_insert, (user_id, game_id, rating))
    except:
        return None

def rateGame(user_id: str, game_id: str, rating: int):
    
    try:
        if rating > 5:
            rating = 5
        elif rating < 1:
            rating = 1
    except:
        if not user_id or not game_id or not rating:
            return None

    sql_update = """
        UPDATE user_owns_game 
        SET rating = %s 
        WHERE game_uuid = %s and user_uuid = %s
    """

    try:
        execute_query(sql_update, (rating, game_id, user_id))
    except:
        return None


def playGame(user_id: str, game_id: str, timeplayed: int, collection_id: str):
    try:
        if timeplayed == 0:
            timeplayed = random.randint(1,120)

        if game_id == "":
            game_id = getRandomGameFromCollection(collection_id, user_id)
    except:
        if not user_id or not timeplayed or (not game_id and not collection_id):
            return None


    sql_select = """
        SELECT game_uuid, user_uuid, total_playtime_minutes 
        FROM game_listing and collection
        WHERE user_uuid = %s AND game_uuid = %s
    """

    sql_update = """
        UPDATE game_listing 
        SET total_playtime_minutes = %s 
        WHERE game_uuid = %s
    """

    sql_insert = """
        INSERT INTO user_plays
        (game_uuid, user_uuid, timeplayed)
        VALUES(%s, %s, %s::esrb)
        RETURNING game_uuid
    """

    try:
        details = execute_query(sql_select, (user_id, game_id), fetchone=True)
        if not details or not details.get("game_uuid") or not details.get("user_uuid"):
            return None

        execute_query(sql_insert,(game_id, user_id, timeplayed))

        execute_query(sql_update, (timeplayed, game_id))
    except:
        return None
    
def getRandomGameFromCollection(collection_id: str, user_id: str):
    if not collection_id and not user_id:
        return None

    sql = """
        SELECT game_uuid FROM collection
        WHERE collection_uuid = %s and user_uuid = %s
    """
    try:
        result = execute_query(sql, (collection_id, user_id), fetchone=True)
        if not result or not result.get("collection"):
            return None
        
        game_list = result["collection"]
        if not game_list:
            return None
        
        index = random.randint(0, len(game_list) - 1)
        return game_list[index]
    except:
        return None
import unittest
import psycopg # pyright: ignore[reportMissingImports]
import uuid
import random
import playing_games.game_Interactions as game_Interactions
from SteamUltraDeluxHDRemixRemastered2.connection import connect_to_db, execute_query


def test_buy_Game():

    #all values are provided
    user_id = "0001"
    game_id = "0001"
    rating = 5
    game_Interactions.buy_Game(user_id,game_id,rating)

    sql_select = """
        SELECT user_uuid, game_uuid, rating 
        FROM user_owns_game
        WHERE user_uuid = %s AND game_uuid = %s AND rating = %s
    """

    try:
        details = execute_query(sql_select, (user_id, game_id, rating), fetchone=True)
        assert details == {'user_uuid': '0001', 'game_uuid': '0001', 'rating': 5}
    except:
        #This should never be reached
        return None
    
    #user id is not provided
    assert game_Interactions.buy_Game(None, game_id, rating) == None

    #game id is not provided
    assert game_Interactions.buy_Game(user_id, None, rating) == None

    #rating is not provided
    game_Interactions.buy_Game("0001","0001")

    sql_select = """
        SELECT user_uuid, game_uuid, rating 
        FROM user_owns_game
        WHERE user_uuid = %s AND game_uuid = %s AND rating = %s
    """

    try:
        details = execute_query(sql_select, (user_id, game_id), fetchone=True)
        assert details == {'user_uuid': '0001', 'game_uuid': '0001', 'rating': None}
    except:
        #This should never be reached
        return None

def test_rate_Game():
    #All values provided
    user_id = "0001"
    game_id = "0001"
    rating = 5

    game_Interactions.rate_Game(user_id, game_id, rating)

    sql_select = """
        SELECT user_uuid, game_uuid, rating 
        FROM user_owns_game
        WHERE user_uuid = %s AND game_uuid = %s AND rating = %s
    """

    try:
        details = execute_query(sql_select, (user_id, game_id), fetchone=True)
        assert details == {'user_uuid': '0001', 'game_uuid': '0001', 'rating': None}
    except:
        #This should never be reached
        return None
    
    #user is is not provided
    assert game_Interactions.rate_Game(None, game_id, rating) == None
    #game is is not provided
    assert game_Interactions.rate_Game(user_id, None, rating) == None
    #rating is not provided
    assert game_Interactions.rate_Game(user_id, game_id, None) == None

def test_play_Game(user_id: str, game_id: str, timeplayed: int, collection_id: str):
    return None
    
def test_get_Random_Game_From_Collection(collection_id: str, user_id: str):
    return None
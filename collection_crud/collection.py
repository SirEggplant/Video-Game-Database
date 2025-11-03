import psycopg # pyright: ignore[reportMissingImports]
import uuid
from db_Connection import execute_query

def create_collection(user_uuid, collection_name):
    sql = """
        INSERT INTO collection
        (collection_uuid, user_uuid, collection_name)
        VALUES(%s,%s, %s)
        RETURNING collection_uuid
    """
    collection_uuid = str(uuid.uuid4())

    try:
        row = execute_query(sql, (collection_uuid, user_uuid, collection_name), fetchone=True)
        return row
    except:
        return None

def list_users_collections(user_uuid: str):
    sql = """
        SELECT * FROM collection
        WHERE user_uuid = %s
        ORDER BY collection_name DESC
    """
    try:
        return execute_query(sql, (user_uuid,), fetchall=True)
    except:
        return None
    
def add_game_to_collection(tokens):
    collection_name = tokens[0]
    game_title = " ".join(tokens[1:])

    game_uuid = get_game_from_title(game_title)    
    collection_uuid = get_collection_from_name(collection_name)
    
    sql_insert = """
        INSERT INTO collection_contains (collection_uuid, game_uuid)
        VALUES (%s, %s)
        RETURNING collection_uuid
    """
    sql_update = """
        UPDATE collection
        SET num_of_games = num_of_games + 1
        WHERE collection_uuid = %s
        RETURNING collection_uuid, num_of_games
    """
    try:
        execute_query(sql_insert, (collection_uuid, game_uuid))
        result=execute_query(sql_update, (collection_uuid,),fetchone=True)
        return result
    except:
        return None
    
def delete_game_from_collection(tokens):
    collection_name = tokens[0]
    game_title = " ".join(tokens[1:])

    game_uuid = get_game_from_title(game_title)
    collection_uuid = get_collection_from_name(collection_name)
    
    sql_delete = """
        DELETE FROM collection_contains
        WHERE collection_uuid = %s AND game_uuid = %s
        RETURNING collection_uuid
    """
    sql_update = """
        UPDATE collection
        SET num_of_games = num_of_games - 1
        WHERE collection_uuid = %s
        RETURNING collection_uuid, num_of_games
    """
    try:
        execute_query(sql_delete, (collection_uuid, game_uuid))
        result = execute_query(sql_update, (collection_uuid,),fetchone=True)
        return result
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
  
def get_collection_from_name(collection_title: str):
    sql_select = """
        SELECT collection_uuid
        FROM collection
        WHERE collection_name ILIKE %s
    """
    
    try:
        pattern = f"%{collection_title}%"
        collection_id = execute_query(sql_select, (pattern,), fetchone=True)
        collection_str = str(collection_id[0])
        if collection_str == "":
            return None
        return collection_str
    except:
        None

def rename_collection(user_uuid: str, old_name: str, new_name: str):
    sql_update = """
        UPDATE collection SET collection_name = %s 
        WHERE user_uuid = %s AND collection_name = %s
        RETURNING *
    """

    row = execute_query(sql_update, (new_name, user_uuid, old_name,), fetchone=True)
    return row

def delete_collection(user_uuid: str, collection_name: str) :
    sql_delete = """
        DELETE FROM collection WHERE
        user_uuid = %s AND collection_name = %s 
    """

    execute_query(sql_delete, (user_uuid, collection_name,))
    return

def check_if_collection_exists(user_uuid: str, collection_name: str):
    sql = """
        SELECT 1 FROM collection WHERE
        user_uuid = %s AND collection_name = %s
        LIMIT 1
    """

    result = execute_query(sql, (user_uuid, collection_name,), fetchone=True)
    return result


def main():
    uuid = "44ecfb56-8c85-4165-b085-fb2ebc53b238"
    # print(create_collection(uuid, "Da Collection"))
    # print(create_collection(uuid, "Da Collection2"))
    # print(list_users_collections(uuid))
    print(add_game_to_collection("2f973766-9419-4118-b397-fe9d7c2c1fe7","f4cdb9e9-83fc-4bbc-bb84-225b34b8e58d"))


if __name__ == "__main__":
    main()
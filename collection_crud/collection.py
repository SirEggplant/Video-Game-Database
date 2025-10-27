import psycopg # pyright: ignore[reportMissingImports]
from SteamUltraDeluxHDRemixRemastered2.connection import connect_to_db, execute_query

def create_collection(user_uuid, collection_name):
    sql = """
        INSERT INTO collection
        (user_uuid, collection_name)
        VALUES(%s, %s)
        RETURNING collection_uuid
    """
    try:
        row = execute_query(sql, (user_uuid, collection_name), fetchone=True)
        return row[0]
    except:
        return None

def list_users_collections(user_uuid: str):
    sql = """
        SELECT * FROM collection
        WHERE user_uuid = %s
    """
    try:
        return execute_query(sql, (user_uuid,), fetchall=True)
    except:
        return None
    
def add_game_to_collection(game_uuid: str, collection_uuid: str):
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
    with connect_to_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_insert, (collection_uuid, game_uuid))
            inserted = cur.fetchone()
            if not inserted:
                return None
            cur.execute(sql_update, (collection_uuid,))
            return cur.fetchone()

def main():
    uuid = "44ecfb56-8c85-4165-b085-fb2ebc53b238"
    # print(create_collection(uuid, "Da Collection"))
    # print(create_collection(uuid, "Da Collection2"))
    # print(list_users_collections(uuid))
    print(add_game_to_collection("2f973766-9419-4118-b397-fe9d7c2c1fe7","f4cdb9e9-83fc-4bbc-bb84-225b34b8e58d"))


if __name__ == "__main__":
    main()
import psycopg
import connection


def get_followers(uuid: str):
    sql = """
        SELECT * FROM follows 
        WHERE followed_user_uuid = %s
    """
    try:
        return connection.execute_query(sql, (uuid,),fetchall=True)
    except:
        return None


def follow(uuid_follower: str, uuid_followed: str):
    sql = """
    INSERT INTO follows(follower_user_uuid, followed_user_uuid) VALUES (%s, %s)
    RETURNING *
"""
    try:
        return connection.execute_query(sql,(uuid_follower, uuid_followed), fetchall=True)
    except:
        return None


def main():
    # print(follow("44ecfb56-8c85-4165-b085-fb2ebc53b238","e254a2c5-83f9-4600-9dc4-5afcd343ff10"))
    print(get_followers("e254a2c5-83f9-4600-9dc4-5afcd343ff10"))


if __name__ =="__main__":
    main()
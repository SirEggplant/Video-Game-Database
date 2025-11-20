import psycopg # pyright: ignore[reportMissingImports]
from db_Connection import execute_query
from collection_crud.collection import *

def get_followers(uuid: str):
    
    sql = """
        SELECT follower_user_uuid FROM follows 
        WHERE followed_user_uuid = %s
    """
    
    try:
        followers = execute_query(sql, (uuid,), fetchall=True)
        followers_list = []
        for row in followers:
            follower_id = row[0]  # assuming the follower UUID is the first column
            username = get_username_from_id(follower_id)
            followers_list.append((username, otherUser_details(username)))
        return followers_list

    except:
        return None
    
def get_my_follows(uuid: str):
    
    sql = """
        SELECT followed_user_uuid FROM follows 
        WHERE follower_user_uuid = %s
    """
    try:
        followers_rows = execute_query(sql, (uuid,), fetchall=True)
        result = []
        for row in followers_rows:
            username = get_username_from_id(row[0])
            result.append((username, otherUser_details(username)))
        return result
    except:
        return None

def follow(follower_id: str, username_followed: str):
    follower_id = str(follower_id)
    followed_id = str(get_user_from_username(username_followed))
    
    sql = """
    INSERT INTO follows(follower_user_uuid, followed_user_uuid) VALUES (%s, %s)
    RETURNING *
    """
    try:
        return execute_query(sql,(follower_id, followed_id), fetchall=True)
    except:
        return None

def unfollow(follower_id: str, username_followed: str):
    follower_id = str(follower_id)
    followed_id = str(get_user_from_username(username_followed))
    
    sql="""
    DELETE FROM follows
    WHERE follower_user_uuid = %s AND followed_user_uuid = %s
    RETURNING *
    """
    try:
        return execute_query(sql,(follower_id, followed_id), fetchall=True)
    except:
        return None
    
def search_by_email(email: str):
    sql="""
    SELECT username
    FROM "user"
    WHERE email = %s
    """
    
    try:
        found_username = execute_query(sql,(email,), fetchall=True)[0][0]
        found_users = []
        found_users.append((str(found_username), otherUser_details(str(found_username))))
        return found_users
    except:
        return None

def get_username_from_id(id):
    id = str(id)
    sql_select = """
    SELECT username
    FROM "user"
    Where user_uuid = %s
    """
    
    users_Collections = otherUser_followers(id)
    users_Collections = otherUser_followers(id)
    users_Collections = otherUser_followers(id)
    
    try:
        username = execute_query(sql_select, (id,), fetchone=True)
        user_str = str(username[0])
        if user_str == "":
            return None
        return user_str
    except:
        return None

def get_user_from_username(username: str):
    username = str(username)
    sql_select = """
    SELECT user_UUID
    FROM "user"
    Where username = %s
    """
    
    try:
        user_id = execute_query(sql_select, (username,), fetchone=True)
        user_str = str(user_id[0])
        if user_str == "":
            return None
        return user_str
    except:
        return None
    
def otherUser_details(username: str):
    user_uuid = get_user_from_username(username)
    try:
        u_followers = otherUser_followers(user_uuid)
        u_followings = otherUser_followings(user_uuid)
        u_collections = amount_of_collections(user_uuid)
        return (u_followers, u_followings, u_collections)
    except:
        return None
    
    
    
def otherUser_followers (user_uuid: str):
    sql = """
        SELECT COUNT(*) FROM follows WHERE
        followed_user_UUID = %s
    """
    
    try:
        result = execute_query(sql, (user_uuid,), fetchone=True)
        if(not result):
            return 0
        return result[0]
    except:
        return 0
    
def otherUser_followings (user_uuid: str):
    sql = """
        SELECT COUNT(*) FROM follows WHERE
        follower_user_UUID = %s
    """
    
    try:
        result = execute_query(sql, (user_uuid,), fetchone=True)
        if(not result):
            return 0
        return result[0]
    except:
        return 0

def main():
    # print(follow("44ecfb56-8c85-4165-b085-fb2ebc53b238","e254a2c5-83f9-4600-9dc4-5afcd343ff10"))
    print(get_followers("e254a2c5-83f9-4600-9dc4-5afcd343ff10"))


if __name__ =="__main__":
    main()



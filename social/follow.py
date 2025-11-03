import psycopg # pyright: ignore[reportMissingImports]
from db_Connection import execute_query

def get_followers(uuid: str):
    
    sql = """
        SELECT followers_user_uuid FROM follows 
        WHERE followed_user_uuid = %s
    """
    
    try:
        followers = execute_query(sql, (uuid,),fetchall=True)
        followers_rows = execute_query(sql, (uuid,), fetchall=True)
        followers_dict = {}
        for row in followers_rows:
            follower_id = row[0]  # assuming the follower UUID is the first column
            followers_dict[follower_id] = get_username_from_id(follower_id)
        return followers_dict

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
            result.append(get_username_from_id(row[0]))
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
    SELECT user_UUID, username, email
    FROM "user"
    Where email ILIKE %s
    """
    
    try:
        pattern = f"%{email}%"
        return execute_query(sql,(pattern,), fetchall=True)[1]
    except:
        return None

def get_username_from_id(id):
    id = str(id)
    sql_select = """
    SELECT username
    FROM "user"
    Where user_uuid = %s
    """
    
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

def main():
    # print(follow("44ecfb56-8c85-4165-b085-fb2ebc53b238","e254a2c5-83f9-4600-9dc4-5afcd343ff10"))
    print(get_followers("e254a2c5-83f9-4600-9dc4-5afcd343ff10"))


if __name__ =="__main__":
    main()



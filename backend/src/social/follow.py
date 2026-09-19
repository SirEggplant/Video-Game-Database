from src.db import execute_query
from src.collections.crud import amount_of_collections


def get_followers(user_uuid: str):
    sql = """
        SELECT follower_user_uuid FROM follows
        WHERE followed_user_uuid = %s
    """
    try:
        followers = execute_query(sql, (user_uuid,), fetchall=True)
        followers_list = []
        for row in followers:
            follower_id = row[0]
            username = get_username_from_id(follower_id)
            followers_list.append((username, other_user_details(username)))
        return followers_list
    except Exception:
        return None


def get_my_follows(user_uuid: str):
    sql = """
        SELECT followed_user_uuid FROM follows
        WHERE follower_user_uuid = %s
    """
    try:
        rows = execute_query(sql, (user_uuid,), fetchall=True)
        result = []
        for row in rows:
            username = get_username_from_id(row[0])
            result.append((username, other_user_details(username)))
        return result
    except Exception:
        return None


def follow(follower_id: str, username_followed: str):
    follower_id = str(follower_id)
    followed_id = str(get_user_from_username(username_followed))

    sql = """
        INSERT INTO follows(follower_user_uuid, followed_user_uuid)
        VALUES (%s, %s)
        RETURNING *
    """
    try:
        return execute_query(sql, (follower_id, followed_id), fetchall=True)
    except Exception:
        return None


def unfollow(follower_id: str, username_followed: str):
    follower_id = str(follower_id)
    followed_id = str(get_user_from_username(username_followed))

    sql = """
        DELETE FROM follows
        WHERE follower_user_uuid = %s AND followed_user_uuid = %s
        RETURNING *
    """
    try:
        return execute_query(sql, (follower_id, followed_id), fetchall=True)
    except Exception:
        return None


def search_by_email(email: str):
    sql = """
        SELECT username
        FROM "user"
        WHERE email = %s
    """
    try:
        found_username = execute_query(sql, (email,), fetchall=True)[0][0]
        return [(str(found_username), other_user_details(str(found_username)))]
    except Exception:
        return None


def get_username_from_id(user_uuid: str):
    user_uuid = str(user_uuid)
    sql = """
        SELECT username
        FROM "user"
        WHERE user_uuid = %s
    """
    try:
        username = execute_query(sql, (user_uuid,), fetchone=True)
        if not username:
            return None
        user_str = str(username[0])
        return user_str if user_str else None
    except Exception:
        return None


def get_user_from_username(username: str):
    username = str(username)
    sql = """
        SELECT user_uuid
        FROM "user"
        WHERE username = %s
    """
    try:
        user_id = execute_query(sql, (username,), fetchone=True)
        if not user_id:
            return None
        user_str = str(user_id[0])
        return user_str if user_str else None
    except Exception:
        return None


def other_user_details(username: str):
    user_uuid = get_user_from_username(username)
    try:
        u_followers = other_user_followers(user_uuid)
        u_followings = other_user_followings(user_uuid)
        u_collections = amount_of_collections(user_uuid)
        return (u_followers, u_followings, u_collections)
    except Exception:
        return None


def other_user_followers(user_uuid: str):
    sql = """
        SELECT COUNT(*) FROM follows
        WHERE followed_user_uuid = %s
    """
    try:
        result = execute_query(sql, (user_uuid,), fetchone=True)
        return result[0] if result else 0
    except Exception:
        return 0


def other_user_followings(user_uuid: str):
    sql = """
        SELECT COUNT(*) FROM follows
        WHERE follower_user_uuid = %s
    """
    try:
        result = execute_query(sql, (user_uuid,), fetchone=True)
        return result[0] if result else 0
    except Exception:
        return 0

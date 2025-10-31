import psycopg # pyright: ignore[reportMissingImports]
import uuid
<<<<<<< HEAD
from src.db_Connection import connect_to_db, execute_query
=======
from db_Connection import connect_to_db, execute_query

>>>>>>> b3f8b53428799462283b0486ff9317744588338b


def login_with_user(username: str, password: str):

    sql_select = """
        SELECT user_uuid FROM "user" WHERE username = %s AND password = %s
    """

    sql_update = """
        UPDATE "user" SET last_access_date = CURRENT_DATE 
        WHERE username = %s
"""

    conn, server = connect_to_db()
    if not conn or not server:
        return None

    try:
        with conn.cursor() as cur:
            cur.execute(sql_select, (username, password))
            result = cur.fetchone()
            cur.execute(sql_update, (username,))
            conn.commit()
            return result
    except Exception as e:
        print("Error executing query:", e)
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass
        try:
            server.stop()
        except Exception:
            pass
            
def login_with_email(email: str, password: str):

    sql_select = """
        SELECT * FROM "user" WHERE email = %s AND password = %s
    """

    sql_update = """
        UPDATE "user" SET last_access_date = CURRENT_DATE 
        WHERE email = %s
"""

    conn, server = connect_to_db()
    if not conn or not server:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(sql_select, (email, password))
            result = cur.fetchone()
            cur.execute(sql_update, (email,))
            conn.commit()
            return result
    except Exception as e:
        print("Error executing query:", e)
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass
        try:
            server.stop()
        except Exception:
            pass
    
    
def register(username, password, firstname, lastname, email):

    sql_insert = """
        INSERT INTO "user"
        (user_uuid, username, password, first_name, last_name, email, total_playtime, creation_date, last_access_date)
        VALUES (%s, %s, %s, %s, %s, %s, 0, CURRENT_DATE, CURRENT_DATE)
        RETURNING * 
    """
    user_id = str(uuid.uuid4())

    try:
        value = execute_query(sql_insert, (user_id,username, password, firstname, lastname, email), fetchone=True)
        return value
    except:
        return None
            



def main():
    # print(register("teteo1", "mmrk", "seb", "canakis", "sebastian1.canakis@gmail.com"))
    # print(register("teteo2", "mmrk", "seb", "canakis", "sebastian2.canakis@gmail.com"))

    print(login_with_user("teteo1", "mmrk"))
    print(login_with_email("sebastian1.canakis@gmail.com", "mmrk"))


if __name__ == "__main__":
    main()


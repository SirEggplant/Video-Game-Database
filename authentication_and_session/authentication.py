import psycopg # pyright: ignore[reportMissingImports]
import uuid
from db_Connection import execute_query



def login_with_user(username: str, password: str):

    sql_select = """
        SELECT * FROM "user" WHERE username = %s AND password = %s
    """

    sql_update = """
        UPDATE "user" SET last_access_date = CURRENT_DATE 
        WHERE username = %s
"""

    

    try:
        result = execute_query(sql_select, (username, password), fetchone=True)
        if result is None:
            return None
        execute_query(sql_update, (username,))
        return result
    except Exception as e:
        print("Error executing query:", e)
        return None
            
def login_with_email(email: str, password: str):

    sql_select = """
        SELECT * FROM "user" WHERE email = %s AND password = %s
    """

    sql_update = """
        UPDATE "user" SET last_access_date = CURRENT_DATE 
        WHERE email = %s
"""

    
    try:
        result = execute_query(sql_select, (email, password),fetchone=True)
        if result is None:
            return None
        execute_query(sql_update, (email,))
        return result
    except Exception as e:
        print("Error executing query:", e)
        return None
    
    
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


import psycopg # pyright: ignore[reportMissingImports]
from SteamUltraDeluxHDRemixRemastered2.connection import connect_to_db, execute_query



def login_with_user(username, password):

    sql_select = """
        SELECT user_uuid FROM "user" WHERE username = %s AND password = %s
    """

    sql_update = """
        UPDATE "user" SET last_access_date = CURRENT_DATE 
        WHERE username = %s
"""

    with connect_to_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_select, (username, password))
            inserted = cur.fetchone()
            if not inserted:
                return None
            cur.execute(sql_update, (username,))
            return inserted

            
def login_with_email(email, password):

    sql_select = """
        SELECT user_uuid FROM "user" WHERE email = %s AND password = %s
    """

    sql_update = """
        UPDATE "user" SET last_access_date = CURRENT_DATE 
        WHERE email = %s
"""

    with connect_to_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_select, (email, password))
            inserted = cur.fetchone()
            if not inserted:
                return None
            cur.execute(sql_update, (email,))
            return inserted
    
    
def register(username, password, firstname, lastname, email):

    sql_insert = """
        INSERT INTO "user"
        (username, password, first_name, last_name, email, total_playtime, creation_date, last_access_date)
        VALUES (%s, %s, %s, %s, %s, 0, CURRENT_DATE, CURRENT_DATE)
        RETURNING user_uuid
    """


    try:
        value = execute_query(sql_insert, (username, password, firstname, lastname, email), fetchone=True)
        return value[0]
    except:
        return None
            



def main():
    # print(register("teteo1", "mmrk", "seb", "canakis", "sebastian1.canakis@gmail.com"))
    # print(register("teteo2", "mmrk", "seb", "canakis", "sebastian2.canakis@gmail.com"))

    print(login_with_user("teteo1", "mmrk"))
    print(login_with_email("sebastian1.canakis@gmail.com", "mmrk"))


if __name__ == "__main__":
    main()


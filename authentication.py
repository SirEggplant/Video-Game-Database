import psycopg
import connection


def login_with_user(username, password):

    conn = connection.connect_to_db()
    query = """
        SELECT user_uuid FROM "user" WHERE username = %s AND password = %s
    """

    value = connection.execute_query(query, (username, password))
    return value[0]

            
def login_with_email(email, password):

    conn = connection.connect_to_db()
    query = """
        SELECT user_uuid FROM "user" WHERE email = %s AND password = %s
    """

    try:
        value = connection.execute_query(query, (email, password))
        return value[0]
    except:
        return None
    
    
def register(username, password, firstname, lastname, email):

    sql_insert = """
        INSERT INTO "user"
        (username, password, first_name, last_name, email, total_playtime, creation_date, last_access_date)
        VALUES (%s, %s, %s, %s, %s, 0, CURRENT_DATE, CURRENT_DATE)
        RETURNING user_uuid
    """


    try:
        value = connection.execute_query(sql_insert, (username, password, firstname, lastname, email))
        return value[0]
    except:
        return None
            



def main():
    print(register("teteo1", "mmrk", "seb", "canakis", "sebastian1.canakis@gmail.com"))
    print(login_with_user("teteo1", "mmrk"))


if __name__ == "__main__":
    main()


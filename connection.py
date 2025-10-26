import psycopg


def connect_to_db():
    try:
        conn = psycopg.connect(
            dbname="p320_46",
            user="",          # <- DB user only
            password="",
            host="localhost",
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None
    


def execute_query(sql, tuple):

    with connect_to_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql, tuple)
                new_row = cur.fetchone()
                if new_row:
                    return new_row
                return None
            except:
                return None

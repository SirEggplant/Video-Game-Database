import psycopg # pyright: ignore[reportMissingImports]


def connect_to_db():
    try:
        conn = psycopg.connect(
            dbname="p320_46",
            user="",          
            password="",
            host="localhost",
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None
    

# TODO: CLOSE CONNECTION
def execute_query(sql, params=(), fetchone=False, fetchall=False):
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if fetchone:
                    value = cur.fetchone()
                    return value
                if fetchall:
                    values = cur.fetchall()
                    return values
                conn.commit()
                return None
    except Exception as e:
        print("Error executing query:", e)
        return None
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
    


def execute_query(sql, params=(), fetchone=False, fetchall=False):
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if fetchone:
                    return cur.fetchone()
                if fetchall:
                    return cur.fetchall()
                conn.commit()
                return None
    except Exception as e:
        print("Error executing query:", e)
        return None
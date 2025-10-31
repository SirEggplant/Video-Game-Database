import warnings
from cryptography.utils import CryptographyDeprecationWarning # pyright: ignore[reportMissingImports]
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

import psycopg  # pyright: ignore[reportMissingImports]
import os
from sshtunnel import SSHTunnelForwarder # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]

load_dotenv()

#username = os.getenv("USERNAME")
username = input("Username for db: ")
password = input("Password for db: ")
dbName = "p320_46"

def connect_to_db():
    try:
        
        server = SSHTunnelForwarder(
            ('starbug.cs.rit.edu', 22),
            ssh_username=username,
            ssh_password=password,
            remote_bind_address=('127.0.0.1', 5432),
            allow_agent=False,
            host_pkey_directories=[],
        )
        server.start()
        # print("SSH tunnel established")

        conn = psycopg.connect(
            dbname=dbName,
            user=username,
            password=password,
            host='localhost',
            port=server.local_bind_port
        )
        # print("Database connection established")

        return conn, server
    except Exception as e:
        print("Connection failed:", repr(e))
        return None, None


def execute_query(sql, params=(), fetchone=False, fetchall=False):
    conn, server = connect_to_db()
    if not conn or not server:
        return None

    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result = None
            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()
            conn.commit()
            return result
    except Exception as e:
        # print("Error executing query:", e)
        return None
    finally:
        try:
            conn.close()
            # print("Database connection closed.")
        except Exception:
            pass
        try:
            server.stop()
            # print("SSH tunnel closed.")
        except Exception:
            pass


def main():
    result = execute_query("SELECT version();", fetchone=True)
    print("Result:", result)


if __name__ == "__main__":
    main()

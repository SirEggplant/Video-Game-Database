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

_conn = None
_server = None

def connect_to_db():
    global _conn, _server
    
    # Reuse existing connection if available
    if _conn is not None and not _conn.closed:
        return _conn, _server
    
    # Create new connection
    try:
        _server = SSHTunnelForwarder(
            ('starbug.cs.rit.edu', 22),
            ssh_username=username,
            ssh_password=password,
            remote_bind_address=('127.0.0.1', 5432),
            allow_agent=False,
            host_pkey_directories=[],
        )
        _server.start()

        _conn = psycopg.connect(
            dbname=dbName,
            user=username,
            password=password,
            host='localhost',
            port=_server.local_bind_port
        )
        return _conn, _server
    except Exception as e:
        print("Connection failed:", repr(e))
        return None, None


def close_connection():
    global _conn, _server
    try:
        if _conn:
            _conn.close()
            _conn = None
    except:
        pass
    try:
        if _server:
            _server.stop()
            _server = None
    except:
        pass


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



def main():
    result = execute_query("SELECT version();", fetchone=True)
    print("Result:", result)
    close_connection()


if __name__ == "__main__":
    main()

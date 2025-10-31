import warnings
from cryptography.utils import CryptographyDeprecationWarning  # pyright: ignore[reportMissingImports]
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

import psycopg  # pyright: ignore[reportMissingImports]
import os
from sshtunnel import SSHTunnelForwarder  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

import getpass

load_dotenv()

#username = os.getenv("USERNAME")
username = "jnd6300" #input("Username for db: ")
password = "HuesOfRed-2022" #getpass.getpass("Password for db: ")
dbName = "p320_46"

def setup_connections():
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
        conn = psycopg.connect(
            dbname=dbName,
            user=username,
            password=password,
            host='localhost',
            port=server.local_bind_port
        )
        return conn, server
    except Exception as e:
        print("Connection failed:", repr(e))
        return None, None


def execute_query(sql, params=(), fetchone=False, fetchall=False):
    conn, server = connect_to_db()
    if not conn or not server:
        print("Failed to establish DB connection")
        return None

    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result = None
            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()

            # Commit only if modifying data
            if sql.strip().lower().startswith(("insert", "update", "delete")):
                conn.commit()

            return result
    except Exception as e:
        print(f"Error executing query: {e}")
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


def close_connections(conn, server):
    try:
        conn.close()
    except Exception:
        pass
    try:
        server.stop()
    except Exception:
        pass

def main():
    conn, server = setup_connections()
    if not conn or not server:
        return
    result = execute_query(conn, "SELECT version();", fetchone=True)
    print("Result:", result)
    # You can execute more queries here using the same conn
    # result2 = execute_query(conn, "SELECT * FROM table;", fetchall=True)
    close_connections(conn, server)

if __name__ == "__main__":
    main()

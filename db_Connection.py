import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

import psycopg
import os
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
import getpass

load_dotenv()

username = input("Username for db: ")
password = getpass.getpass("Password for db: ")
dbName = "p320_46"

# Module-level variables to hold persistent connection and SSH tunnel
conn = None
server = None

def setup_connections():
    global conn, server
    if conn is not None and server is not None:
        # Connection already exists
        return conn, server
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
        conn = None
        server = None
        return None, None

def execute_query(sql, params=(), fetchone=False, fetchall=False):
    global conn, server
    if conn is None or server is None:
        conn, server = setup_connections()
    if conn is None or server is None:
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
            conn.commit()

            return result
    except (psycopg.errors.AdminShutdown, psycopg.errors.ConnectionException, psycopg.InterfaceError) as e:
        # Handle connection closed or timeout exceptions by reconnecting once
        print(f"Connection error detected: {e}, reconnecting...")
        close_connections()
        conn, server = setup_connections()
        if conn is None or server is None:
            print("Failed to re-establish DB connection after error")
            return None

        # Retry the query once after reconnecting
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                result = None
                if fetchone:
                    result = cur.fetchone()
                elif fetchall:
                    result = cur.fetchall()
                if sql.strip().lower().startswith(("insert", "update", "delete")):
                    conn.commit()
                return result
        except Exception as e2:
            print(f"Error executing query after reconnect: {e2}")
            return None
    except Exception as e:
        print(f"Error executing query: {e}")
        try:
            conn.rollback()
        except:
            pass
        return None


def close_connections():
    global conn, server
    try:
        if conn is not None:
            conn.close()
            conn = None
    except Exception:
        pass
    try:
        if server is not None:
            server.stop()
            server = None
    except Exception:
        pass

def main():
    conn, server = setup_connections()
    if conn is None or server is None:
        return
    result = execute_query("SELECT version();", fetchone=True)
    print("Result:", result)
    # Execute more queries here using execute_query(...)
    close_connections()

if __name__ == "__main__":
    main()

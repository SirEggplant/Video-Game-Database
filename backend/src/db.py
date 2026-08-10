import os
import psycopg
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Module-level persistent connection
_conn = None

def get_connection():
    """Returns a persistent database connection."""
    global _conn

    # If connection exists and is still open, reuse it
    if _conn is not None and not _conn.closed:
        return _conn

    # Otherwise, create a new connection
    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set in .env file")

    try:
        _conn = psycopg.connect(DATABASE_URL)
        return _conn
    except Exception as e:
        print(f"Connection failed: {repr(e)}")
        return None

def execute_query(sql, params=(), fetchone=False, fetchall=False):
    """Execute a SQL query with optional parameters."""
    conn = get_connection()
    if conn is None:
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
    except Exception as e:
        print(f"Error executing query: {e}")
        try:
            conn.rollback()
        except:
            pass
        return None

def close_connection():
    """Close the persistent database connection."""
    global _conn
    if _conn is not None:
        try:
            _conn.close()
        except:
            pass
        _conn = None

# For backward compatibility with existing code
def close_connections():
    close_connection()

# For backward compatibility with existing code
def setup_connections():
    conn = get_connection()
    return conn, None  # server is no longer needed

def main():
    """Test the connection."""
    result = execute_query("SELECT version();", fetchone=True)
    if result:
        print("✅ Connected to:", result[0])
    else:
        print("❌ Connection failed")
    close_connection()

if __name__ == "__main__":
    main()
import psycopg # pyright: ignore[reportMissingImports]
import uuid
from connection import execute_query

esrbs = {'Early Childhood',
      'Everyone',
      'Everyone 10+',
      'Teen',
      'Mature 17+',
      'Adults Only 18+',
      'Rating Pending'}


SQL_STORED = ""
PARAMS_STORED = ""

def apply_regular_order(sql: str, params, fetchall = False):
    sql = sql + f" ORDER BY title, release_year ASC" 
    
    try:
        rows = execute_query(sql=sql, params=params, fetchall=fetchall)
        return rows
    except Exception as e:
        print(f"Error fetching games by genre: {e}")
        return None

def store_previous_sql_query(sql: str, params):
    global SQL_STORED, PARAMS_STORED

    SQL_STORED = sql
    PARAMS_STORED = params

def sort_by(field: str, order: str):
    lower_field = field.lower()
    actual_field = ""
    match lower_field:
        case "year":
            actual_field = "release_year"
        case "price":
            actual_field = "min_price"
        case _:
            actual_field = field

    sql = SQL_STORED + f" ORDER BY {actual_field}" 
    if order.lower() == "desc":
        sql += " DESC"
    else:
        sql += " ASC"
    try:
        rows = execute_query(sql=sql, params=PARAMS_STORED, fetchall=True)
        return rows
    except Exception as e:
        print(f"Error fetching games by genre: {e}")
        return None

def create_game(game_title: str, game_description: str, game_esrb : str):

    if game_esrb not in esrbs:
        return None

    sql = """
        INSERT INTO game
        (game_uuid, title, game_description, esrb_rating)
        VALUES(%s, %s, %s::esrb)
        RETURNING game_uuid
    """
    try:
        row = execute_query(sql, (str(uuid.uuid4()),game_title, game_description, game_esrb), fetchone=True)
        return row[0]
    except:
        return None

def get_game_by_uuid(game_uuid : str):

    sql = """
        SELECT * FROM game_listing AS 
        
        WHERE game_uuid = %s
    """

    try:
        row = execute_query(sql, (game_uuid,), fetchone=True)
        return row
    except:
        return None


def get_game_by_title(tokens):

    title = " ".join(tokens[3:]).strip()
    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
               total_playtime_minutes, esrb_rating, total_user_rating,
               first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE title ILIKE %s
    """

    try:
        rows = apply_regular_order(sql=sql, params=(f"%{title}%",), fetchall=True)
        store_previous_sql_query(sql=sql, params=(f"%{title}%",))
        return rows
    except:
        return None
    
def get_game_by_genre(genre :str):
    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE game_uuid IN (
            SELECT g.game_uuid
            FROM game AS g
            JOIN game_fits_in_genre AS gg ON gg.game_uuid = g.game_uuid
            JOIN genre ON gg.genre_uuid = genre.genre_uuid
            WHERE genre.genre_name ILIKE %s
        )
    """

    try:
        rows = apply_regular_order(sql, (f"%{genre}%",), fetchall=True)
        store_previous_sql_query(sql=sql, params=(f"%{genre}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by genre: {e}")
        return None


def get_game_by_platform(platform: str):
    sql = """

        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE game_uuid IN (
            SELECT g.game_uuid
            FROM game AS g
            JOIN game_release AS gr ON g.game_uuid = gr.game_uuid
            JOIN platform AS p ON p.platform_uuid = gr.platform_uuid
            WHERE p.platform_name ILIKE %s
        )

    """

    try:
        rows = apply_regular_order(sql, (f"%{platform}%",), fetchall=True)
        store_previous_sql_query(sql=sql, params=(f"%{platform}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by platform: {e}")
        return None
    

def get_game_by_release_year(year: str):
    sql = """

        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
            WHERE game_uuid IN (
            SELECT g.game_uuid
            FROM game AS g
            JOIN game_release AS gr ON g.game_uuid = gr.game_uuid
            WHERE EXTRACT ( YEAR FROM gr.release_date) = %s)
    """

    try:
        rows = apply_regular_order(sql, (year,), fetchall=True)
        store_previous_sql_query(sql=sql, params=(year,))
        return rows
    except Exception as e:
        print(f"Error fetching games by release year: {e}")
        return None

def get_game_by_developer(tokens):

    developer = " ".join(tokens[3:]).strip()

    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE game_uuid IN (
        SELECT g.game_uuid
        FROM game AS g
        JOIN develops AS d ON d.game_uuid = g.game_uuid
        JOIN contributor AS c ON c.contributor_uuid = d.contributor_uuid
        WHERE c.contributor_name ILIKE %s)
    """

    try:
        rows = apply_regular_order(sql, (f"%{developer}%",), fetchall=True)
        store_previous_sql_query(sql=sql, params=(f"%{developer}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by developer: {e}")
        return None

def get_game_by_publisher(tokens):
    publisher = " ".join(tokens[3:]).strip()

    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE game_uuid IN (
        SELECT g.game_uuid
        FROM game AS g
        JOIN publishes AS p ON p.game_uuid = g.game_uuid
        JOIN contributor AS c ON c.contributor_uuid = p.contributor_uuid
        WHERE c.contributor_name ILIKE %s)
    """

    try:
        rows = apply_regular_order(sql, (f"%{publisher}%",), fetchall=True)
        store_previous_sql_query(sql=sql, params=(f"%{publisher}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by developer: {e}")
        return None

    
def get_game_by_price_lower_than(price: str):
    
    intPrice = int(price)

    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE game_uuid IN (
        SELECT g.game_uuid
        FROM game AS g
        JOIN game_release AS r ON g.game_uuid = r.game_uuid
        WHERE r.price < %s)
    """

    try:
        rows = apply_regular_order(sql, (intPrice,), fetchall=True)
        store_previous_sql_query(sql=sql, params=(intPrice,))
        return rows
    except Exception as e:
        print(f"Error fetching games by developer: {e}")
        return None

def get_game_by_price_between(lower_price: str, upper_price: str):

    actual_lower = int(lower_price)
    actual_upper= int(upper_price)

    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE game_uuid IN (
        SELECT g.game_uuid
        FROM game AS g
        JOIN game_release AS r ON g.game_uuid = r.game_uuid
        WHERE r.price BETWEEN %s AND %s)
    """

    try:
        rows = apply_regular_order(sql, (actual_lower, actual_upper,), fetchall=True)
        store_previous_sql_query(sql=sql, params=(actual_lower, actual_upper,))
        return rows
    except Exception as e:
        print(f"Error fetching games by developer: {e}")
        return None

def get_games_by_esrb(esrb: str):
    sql = """
    SELECT game_uuid, title, platforms, developers, publishers,
        total_playtime_minutes, esrb_rating, total_user_rating,
        first_release_date, release_year, min_price, max_price, genres
    FROM game_listing
    WHERE esrb_rating::text ILIKE %s
"""
    try:
        rows = apply_regular_order(sql=sql, params=(f"%{esrb}%",), fetchall=True)    
        store_previous_sql_query(sql=sql, params=(f"%{esrb}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by developer: {e}")
        return None
   

def main():
    pass

if __name__ == "__main__":
    main()



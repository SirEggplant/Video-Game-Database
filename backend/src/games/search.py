import psycopg  # pyright: ignore[reportMissingImports]
import uuid
from typing import Optional, Dict, Any
from src.db import execute_query

esrbs = {
    'Early Childhood',
    'Everyone',
    'Everyone 10+',
    'Teen',
    'Mature 17+',
    'Adults Only 18+',
    'Rating Pending'
}

SQL_STORED = ""
PARAMS_STORED = ""


def apply_regular_order(sql: str, params, fetchall=False):
    sql = sql + f" ORDER BY title, release_year ASC"
    try:
        rows = execute_query(sql=sql, params=params, fetchall=fetchall)
        return rows
    except Exception as e:
        print(f"Error fetching games: {e}")
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
        print(f"Error sorting games: {e}")
        return None


def create_game(game_title: str, game_description: str, game_esrb: str):
    if game_esrb not in esrbs:
        return None
    sql = """
        INSERT INTO game
        (game_uuid, title, game_description, esrb_rating)
        VALUES(%s, %s, %s::esrb)
        RETURNING game_uuid
    """
    try:
        row = execute_query(sql, (str(uuid.uuid4()), game_title, game_description, game_esrb), fetchone=True)
        return row[0]
    except:
        return None


def get_game_by_uuid(game_uuid: str):
    sql = """
        SELECT * FROM game_listing
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


def get_game_by_genre(genre: str):
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
            WHERE EXTRACT(YEAR FROM gr.release_date) = %s
        )
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
            WHERE c.contributor_name ILIKE %s
        )
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
            WHERE c.contributor_name ILIKE %s
        )
    """
    try:
        rows = apply_regular_order(sql, (f"%{publisher}%",), fetchall=True)
        store_previous_sql_query(sql=sql, params=(f"%{publisher}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by publisher: {e}")
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
            WHERE r.price < %s
        )
    """
    try:
        rows = apply_regular_order(sql, (intPrice,), fetchall=True)
        store_previous_sql_query(sql=sql, params=(intPrice,))
        return rows
    except Exception as e:
        print(f"Error fetching games by price: {e}")
        return None


def get_game_by_price_between(lower_price: str, upper_price: str):
    actual_lower = int(lower_price)
    actual_upper = int(upper_price)
    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE game_uuid IN (
            SELECT g.game_uuid
            FROM game AS g
            JOIN game_release AS r ON g.game_uuid = r.game_uuid
            WHERE r.price BETWEEN %s AND %s
        )
    """
    try:
        rows = apply_regular_order(sql, (actual_lower, actual_upper,), fetchall=True)
        store_previous_sql_query(sql=sql, params=(actual_lower, actual_upper,))
        return rows
    except Exception as e:
        print(f"Error fetching games by price: {e}")
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
        print(f"Error fetching games by ESRB: {e}")
        return None


def get_game_all(limit: Optional[int] = None, offset: Optional[int] = 0):
    """
    Fetch all games with optional pagination.
    """
    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
            total_playtime_minutes, esrb_rating, total_user_rating,
            first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        ORDER BY title ASC
    """
    params = []
    if limit is not None:
        sql += " LIMIT %s OFFSET %s"
        params.append(limit)
        params.append(offset)
    try:
        rows = execute_query(sql=sql, params=params, fetchall=True)
        return rows
    except Exception as e:
        print(f"Error fetching all games: {e}")
        return None


def get_game_uuid_by_title(game_title: str):
    """
    Simple function to get game UUID by title
    """
    sql = """
        SELECT game_uuid, title
        FROM game_listing
        WHERE title ILIKE %s
        LIMIT 1
    """
    try:
        row = execute_query(sql, (f"%{game_title}%",), fetchone=True)
        if row:
            return row[0]
    except Exception as e:
        print(f"Error: {e}")
        return None


def search_games(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    platform: Optional[str] = None,
    contributor: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Unified search function with pagination.
    Returns:
        {
            "results": [...],
            "total": <total count>
        }
    """
    conditions = []
    params = []

    if title:
        conditions.append("title ILIKE %s")
        params.append(f"%{title}%")
    if genre:
        conditions.append("""
            EXISTS (
                SELECT 1
                FROM game_fits_in_genre gfg
                JOIN genre g ON gfg.genre_uuid = g.genre_uuid
                WHERE gfg.game_uuid = game_listing.game_uuid
                AND g.genre_name ILIKE %s
            )
        """)
        params.append(f"%{genre}%")
    if platform:
        conditions.append("""
            EXISTS (
                SELECT 1
                FROM game_release gr
                JOIN platform p ON gr.platform_uuid = p.platform_uuid
                WHERE gr.game_uuid = game_listing.game_uuid
                AND p.platform_name ILIKE %s
            )
        """)
        params.append(f"%{platform}%")
    if contributor:
        conditions.append("""
            EXISTS (
                SELECT 1
                FROM develops d
                JOIN contributor c ON d.contributor_uuid = c.contributor_uuid
                WHERE d.game_uuid = game_listing.game_uuid
                AND c.contributor_name ILIKE %s
            )
        """)
        params.append(f"%{contributor}%")

    where_clause = " AND ".join(conditions) if conditions else "TRUE"

    # Count total matching games – use game_listing, not game!
    count_sql = f"SELECT COUNT(*) FROM game_listing WHERE {where_clause};"
    total = execute_query(count_sql, params, fetchone=True)
    total_count = total[0] if total else 0

    # Fetch paginated results from game_listing
    sql = f"""
        SELECT game_uuid, title, platforms, developers, publishers,
               total_playtime_minutes, esrb_rating, total_user_rating,
               first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE {where_clause}
        ORDER BY title ASC
        LIMIT %s OFFSET %s;
    """
    params.extend([limit, offset])
    results = execute_query(sql, params, fetchall=True)

    return {
        "results": results if results else [],
        "total": total_count
    }


def main():
    pass


if __name__ == "__main__":
    main()
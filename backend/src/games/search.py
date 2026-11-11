"""Game search and retrieval functions."""

import uuid
from typing import Any, Optional

from src.db import execute_query

ESRBS = {
    "Early Childhood",
    "Everyone",
    "Everyone 10+",
    "Teen",
    "Mature 17+",
    "Adults Only 18+",
    "Rating Pending",
}

# Whitelist of allowed sort fields to prevent SQL injection.
_SORT_FIELD_MAP = {
    "title": "title",
    "year": "release_year",
    "price": "min_price",
    "genre": "genres",
    "esrb": "esrb_rating",
    "rating": "total_user_rating",
}

SQL_STORED = ""
PARAMS_STORED = ""


def _apply_regular_order(sql: str, params, fetchall=False):
    """Append the default ORDER BY clause and execute the query."""
    sql = sql + " ORDER BY title, release_year ASC"
    try:
        return execute_query(sql=sql, params=params, fetchall=fetchall)
    except Exception as e:
        print(f"Error fetching games: {e}")
        return None


def store_previous_sql_query(sql: str, params):
    """Remember the last query so ``sort_by`` can re-sort the results."""
    global SQL_STORED, PARAMS_STORED
    SQL_STORED = sql
    PARAMS_STORED = params


def sort_by(field: str, order: str):
    """Re-run the previous query with a different sort field and direction."""
    actual_field = _SORT_FIELD_MAP.get(field.lower())
    if not actual_field:
        print(f"Invalid sort field: {field}")
        return None

    sql = SQL_STORED + f" ORDER BY {actual_field}"
    sql += " DESC" if order.lower() == "desc" else " ASC"
    try:
        return execute_query(sql=sql, params=PARAMS_STORED, fetchall=True)
    except Exception as e:
        print(f"Error sorting games: {e}")
        return None


def create_game(game_title: str, game_description: str, game_esrb: str):
    """Insert a new game and return its UUID."""
    if game_esrb not in ESRBS:
        return None
    sql = """
        INSERT INTO game (game_uuid, title, game_description, esrb_rating)
        VALUES (%s, %s, %s::esrb)
        RETURNING game_uuid
    """
    try:
        row = execute_query(
            sql, (str(uuid.uuid4()), game_title, game_description, game_esrb), fetchone=True
        )
        return row[0] if row else None
    except Exception:
        return None


def get_game_by_uuid(game_uuid: str):
    """Return a single game row by UUID."""
    sql = "SELECT * FROM game_listing WHERE game_uuid = %s"
    try:
        return execute_query(sql, (game_uuid,), fetchone=True)
    except Exception:
        return None


def get_game_by_title(tokens):
    """Return games whose title matches the given tokens (partial match)."""
    title = " ".join(tokens[3:]).strip()
    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
               total_playtime_minutes, esrb_rating, total_user_rating,
               first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE title ILIKE %s
    """
    try:
        rows = _apply_regular_order(sql, (f"%{title}%",), fetchall=True)
        store_previous_sql_query(sql, (f"%{title}%",))
        return rows
    except Exception:
        return None


def get_game_by_genre(genre: str):
    """Return games matching the given genre."""
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
        rows = _apply_regular_order(sql, (f"%{genre}%",), fetchall=True)
        store_previous_sql_query(sql, (f"%{genre}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by genre: {e}")
        return None


def get_game_by_platform(platform: str):
    """Return games available on the given platform."""
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
        rows = _apply_regular_order(sql, (f"%{platform}%",), fetchall=True)
        store_previous_sql_query(sql, (f"%{platform}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by platform: {e}")
        return None


def get_game_by_release_year(year: str):
    """Return games released in the given year."""
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
        rows = _apply_regular_order(sql, (year,), fetchall=True)
        store_previous_sql_query(sql, (year,))
        return rows
    except Exception as e:
        print(f"Error fetching games by release year: {e}")
        return None


def get_game_by_developer(tokens):
    """Return games developed by a contributor matching the given tokens."""
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
        rows = _apply_regular_order(sql, (f"%{developer}%",), fetchall=True)
        store_previous_sql_query(sql, (f"%{developer}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by developer: {e}")
        return None


def get_game_by_publisher(tokens):
    """Return games published by a contributor matching the given tokens."""
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
        rows = _apply_regular_order(sql, (f"%{publisher}%",), fetchall=True)
        store_previous_sql_query(sql, (f"%{publisher}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by publisher: {e}")
        return None


def get_game_by_price_lower_than(price: str):
    """Return games with a release price below the given value."""
    int_price = int(price)
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
        rows = _apply_regular_order(sql, (int_price,), fetchall=True)
        store_previous_sql_query(sql, (int_price,))
        return rows
    except Exception as e:
        print(f"Error fetching games by price: {e}")
        return None


def get_game_by_price_between(lower_price: str, upper_price: str):
    """Return games with a release price between two values."""
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
        rows = _apply_regular_order(sql, (actual_lower, actual_upper), fetchall=True)
        store_previous_sql_query(sql, (actual_lower, actual_upper))
        return rows
    except Exception as e:
        print(f"Error fetching games by price: {e}")
        return None


def get_games_by_esrb(esrb: str):
    """Return games with the given ESRB rating."""
    sql = """
        SELECT game_uuid, title, platforms, developers, publishers,
               total_playtime_minutes, esrb_rating, total_user_rating,
               first_release_date, release_year, min_price, max_price, genres
        FROM game_listing
        WHERE esrb_rating::text ILIKE %s
    """
    try:
        rows = _apply_regular_order(sql, (f"%{esrb}%",), fetchall=True)
        store_previous_sql_query(sql, (f"%{esrb}%",))
        return rows
    except Exception as e:
        print(f"Error fetching games by ESRB: {e}")
        return None


def get_game_all(limit: Optional[int] = None, offset: int = 0):
    """Fetch all games with optional pagination."""
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
        params.extend([limit, offset])
    try:
        return execute_query(sql=sql, params=params, fetchall=True)
    except Exception as e:
        print(f"Error fetching all games: {e}")
        return None


def get_game_uuid_by_title(game_title: str):
    """Return a single game UUID by partial title match."""
    sql = """
        SELECT game_uuid FROM game_listing
        WHERE title ILIKE %s
        LIMIT 1
    """
    try:
        row = execute_query(sql, (f"%{game_title}%",), fetchone=True)
        return row[0] if row else None
    except Exception as e:
        print(f"Error: {e}")
        return None


def search_games(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    platform: Optional[str] = None,
    contributor: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Unified search with pagination. Returns ``{"results": [...], "total": N}``."""
    conditions = []
    params = []

    if title:
        conditions.append("title ILIKE %s")
        params.append(f"%{title}%")
    if genre:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM game_fits_in_genre gfg
                JOIN genre g ON gfg.genre_uuid = g.genre_uuid
                WHERE gfg.game_uuid = game_listing.game_uuid
                AND g.genre_name ILIKE %s
            )
        """)
        params.append(f"%{genre}%")
    if platform:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM game_release gr
                JOIN platform p ON gr.platform_uuid = p.platform_uuid
                WHERE gr.game_uuid = game_listing.game_uuid
                AND p.platform_name ILIKE %s
            )
        """)
        params.append(f"%{platform}%")
    if contributor:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM develops d
                JOIN contributor c ON d.contributor_uuid = c.contributor_uuid
                WHERE d.game_uuid = game_listing.game_uuid
                AND c.contributor_name ILIKE %s
            )
        """)
        params.append(f"%{contributor}%")

    where_clause = " AND ".join(conditions) if conditions else "TRUE"

    count_sql = f"SELECT COUNT(*) FROM game_listing WHERE {where_clause};"
    total = execute_query(count_sql, params, fetchone=True)
    total_count = total[0] if total else 0

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

    return {"results": results if results else [], "total": total_count}

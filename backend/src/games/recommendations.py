"""Game recommendation queries for the web API."""

from src.db import execute_query


def get_top_20_games():
    """Return the 20 most-played games in the last 90 days (rolling)."""
    sql = """
        SELECT
            gl.game_uuid,
            gl.title,
            gl.platforms,
            gl.developers,
            gl.publishers,
            SUM(up.time_played) AS playtime_min,
            gl.esrb_rating,
            gl.total_user_rating,
            gl.first_release_date,
            gl.release_year,
            gl.min_price,
            gl.max_price,
            gl.genres
        FROM user_plays up
        JOIN game_listing gl ON gl.game_uuid = up.game_uuid
        WHERE up.played_at >= NOW() - INTERVAL '90 days'
        GROUP BY
            gl.game_uuid, gl.title, gl.platforms, gl.developers, gl.publishers,
            gl.esrb_rating, gl.total_user_rating, gl.first_release_date,
            gl.release_year, gl.min_price, gl.max_price, gl.genres
        ORDER BY playtime_min DESC
        LIMIT 20;
    """
    try:
        return execute_query(sql=sql, fetchall=True)
    except Exception as e:
        print(f"A SQL error occurred getting the top 20 games: {e}")
        return None


def get_top_20_games_of_following(user_uuid: str):
    """Return the 20 most-played games among users the given user follows."""
    sql = """
        SELECT
            gl.game_uuid,
            gl.title,
            gl.platforms,
            gl.developers,
            gl.publishers,
            SUM(up.time_played) AS playtime_min,
            gl.esrb_rating,
            gl.total_user_rating,
            gl.first_release_date,
            gl.release_year,
            gl.min_price,
            gl.max_price,
            gl.genres
        FROM user_plays up
        JOIN follows f ON f.followed_user_uuid = up.user_uuid
        JOIN game_listing gl ON gl.game_uuid = up.game_uuid
        WHERE f.follower_user_uuid = %s
        GROUP BY
            gl.game_uuid, gl.title, gl.platforms, gl.developers, gl.publishers,
            gl.esrb_rating, gl.total_user_rating, gl.first_release_date,
            gl.release_year, gl.min_price, gl.max_price, gl.genres
        ORDER BY playtime_min DESC
        LIMIT 20;
    """
    try:
        return execute_query(sql=sql, params=(user_uuid,), fetchall=True)
    except Exception as e:
        print(f"A SQL error occurred getting the top 20 games of following users: {e}")
        return None


def get_top_5_released():
    """Return the 5 most recently released games from the current month."""
    sql = """
        SELECT
            gl.game_uuid,
            gl.title,
            gl.platforms,
            gl.developers,
            gl.publishers,
            gl.total_playtime_minutes AS playtime_min,
            gl.esrb_rating,
            gl.total_user_rating,
            gl.first_release_date,
            gl.release_year,
            gl.min_price,
            gl.max_price,
            gl.genres
        FROM game_listing gl
        WHERE date_trunc('month', gl.first_release_date)
            = date_trunc('month', CURRENT_DATE)
        ORDER BY gl.first_release_date DESC
        LIMIT 5;
    """
    try:
        return execute_query(sql=sql, fetchall=True)
    except Exception as e:
        print(f"A SQL error occurred getting the top 5 releases: {e}")
        return None


def recommend_games(user_uuid: str):
    """Return up to 20 personalized game recommendations for a user."""
    sql = """
        WITH fav_genres AS (
            SELECT ge.genre_uuid
            FROM user_plays up
            JOIN game_fits_in_genre gf ON gf.game_uuid = up.game_uuid
            JOIN genre ge ON ge.genre_uuid = gf.genre_uuid
            WHERE up.user_uuid = %s
            GROUP BY ge.genre_uuid
            ORDER BY SUM(up.time_played) DESC
            LIMIT 3
        ),
        user_games AS (
            SELECT DISTINCT game_uuid
            FROM user_plays
            WHERE user_uuid = %s
        ),
        candidate_games AS (
            SELECT DISTINCT gf.game_uuid
            FROM game_fits_in_genre gf
            JOIN fav_genres fg ON fg.genre_uuid = gf.genre_uuid
            WHERE gf.game_uuid NOT IN (SELECT game_uuid FROM user_games)
        )
        SELECT
            gl.game_uuid,
            gl.title,
            gl.platforms,
            gl.developers,
            gl.publishers,
            COALESCE(SUM(up.time_played), 0) AS playtime_min,
            gl.esrb_rating,
            COALESCE(AVG(uog.rating), 0) AS avg_rating,
            gl.first_release_date,
            gl.release_year,
            gl.min_price,
            gl.max_price,
            gl.genres
        FROM candidate_games cg
        JOIN game_listing gl ON gl.game_uuid = cg.game_uuid
        LEFT JOIN user_owns_game uog ON uog.game_uuid = cg.game_uuid
        LEFT JOIN user_plays up ON up.game_uuid = cg.game_uuid
        GROUP BY
            gl.game_uuid, gl.title, gl.platforms, gl.developers, gl.publishers,
            gl.esrb_rating, gl.first_release_date,
            gl.release_year, gl.min_price, gl.max_price, gl.genres
        ORDER BY avg_rating DESC, playtime_min DESC
        LIMIT 20;
    """
    try:
        return execute_query(sql=sql, params=(user_uuid, user_uuid), fetchall=True)
    except Exception as e:
        print(f"A SQL error occurred getting the top 20 recommended games: {e}")
        return None

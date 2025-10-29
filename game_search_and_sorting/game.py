import psycopg # pyright: ignore[reportMissingImports]
import uuid
from SteamUltraDeluxHDRemixRemastered2.connection import execute_query

from datetime import date, datetime
from decimal import Decimal

esrb = {'Early Childhood',
      'Everyone',
      'Everyone 10+',
      'Teen',
      'Mature 17+',
      'Adults Only 18+',
      'Rating Pending'}


def create_game(game_title: str, game_description: str, game_esrb : str):

    if game_esrb not in esrb:
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
        ORDER BY title DESC
    """


    try:
        rows = execute_query(sql, (f"%{title}%",), fetchall=True)
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
        rows = execute_query(sql, (f"%{genre}%",), fetchall=True)
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
            ORDER BY g.title DESC
        )

    """

    try:
        rows = execute_query(sql, (f"%{platform}%",), fetchall=True)
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
        rows = execute_query(sql, (year,), fetchall=True)
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
        rows = execute_query(sql, (f"%{developer}%",), fetchall=True)
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
        rows = execute_query(sql, (f"%{publisher}%",), fetchall=True)
       
        return rows
    except Exception as e:
        print(f"Error fetching games by developer: {e}")
        return None

    

def main():

    pass

if __name__ == "__main__":
    main()



# games search <field> <keyword>
#     Search for games by title, genre, platform, release year, developer,
#     publisher, or price range.
#     Example: games search genre RPG
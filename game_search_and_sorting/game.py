import psycopg # pyright: ignore[reportMissingImports]
import uuid
from SteamUltraDeluxHDRemixRemastered2.connection import execute_query


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
        SELECT * FROM game WHERE game_uuid = %s
    """
    try:
        row = execute_query(sql, (game_uuid,), fetchone=True)
        return row
    except:
        return None


def get_game_by_title(title :str):
    sql = """
        SELECT * FROM game 
        WHERE title ILIKE
    """

    try:
        rows = execute_query(sql, (f"%{title}%",), fetchall=True)
        return rows
    except:
        return None
    
def get_game_by_genre(genre :str):
    sql = """
        SELECT g.game_uuid, g.title, g.game_description, g.total_user_rating, g.esrb_rating, g.num_of_players
        FROM game AS g
        JOIN game_fits_in_genre AS gg ON gg.game_uuid = g.game_uuid
        JOIN genre ON gg.genre_uuid = genre.genre_uuid 
        WHERE genre.genre_name = %s;
    """

    try:
        rows = execute_query(sql, (genre,), fetchall=True)
        return rows
    except:
        return None



def main():
    # print(create_game("the game", "it's a game", 'Everyone'))
    # print(get_game('2f973766-9419-4118-b397-fe9d7c2c1fe7'))
    pass

if __name__ == "__main__":
    main()
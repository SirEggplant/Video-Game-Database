from db_Connection import execute_query



def get_top_20_games():
    sql = """
        SELECT(
            gl.game_uuid,
            gl.title,
            gl.esrb_rating,
            gl.total_user_rating,
            gl.platforms,
            gl.genres,
            gl.developers,
            gl.publishers,
            gl.total_playtime_minutes,             
            SUM(up.time_played) AS time_last_90_days
        )
        FROM user_plays up
        JOIN game_listing gl
            ON gl.game_uuid = up.game_uuid
        WHERE up.played_at >= NOW() - INTERVAL '90 days'
        GROUP BY
            gl.game_uuid,
            gl.title,
            gl.esrb_rating,
            gl.total_user_rating,
            gl.platforms,
            gl.genres,
            gl.developers,
            gl.publishers,
            gl.total_playtime_minutes
        ORDER BY time_last_90_days DESC
        LIMIT 20;

    """
    try:
        rows = execute_query(sql=sql, fetchall=True)
        return rows
    except: 
        return None
    
def get_top_20_games_of_following(user_uuid: str):
    sql = """
        SELECT(
            gl.game_uuid,
            gl.title,
            gl.esrb_rating,
            gl.total_user_rating,
            gl.platforms,
            gl.genres,
            gl.developers,
            gl.publishers,
            SUM(up.time_played) AS total_minutes_from_followed
        )
        FROM user_plays up
        JOIN follows f
            ON f.followed_user_uuid = up.user_uuid
        JOIN game_listing gl
            ON gl.game_uuid = up.game_uuid
        WHERE f.follower_user_uuid = :current_user_uuid
        GROUP BY
            gl.game_uuid,
            gl.title,
            gl.esrb_rating,
            gl.total_user_rating,
            gl.platforms,
            gl.genres,
            gl.developers,
            gl.publishers
        ORDER BY total_minutes_from_followed DESC
        LIMIT 20;
    """
    try:
        rows = execute_query(sql=sql,params=(user_uuid,), fetchall=True)
        return rows
    except: 
        return None
    

def get_top_5_released():
    sql = """
    SELECT(
        gl.game_uuid,
        gl.title,
        gl.esrb_rating,
        gl.total_user_rating,
        gl.platforms,
        gl.genres,
        gl.developers,
        gl.publishers,
        gl.first_release_date
    )
    FROM game_listing gl
    WHERE date_trunc('month', gl.first_release_date)
        = date_trunc('month', CURRENT_DATE)
    ORDER BY gl.first_release_date DESC
    LIMIT 5;
    """
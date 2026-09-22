import psycopg # pyright: ignore[reportMissingImports]
from src.db import execute_query

PLATFORM = [
    "pc",
    "playstation 5",
    "playstation",
    "xbox",
    "nintendo switch",
    "xbox series x",
    "xbox series s",
    "xbox series x|s",
]


def add_platform_to_user(user_uuid: str, platform_name: str):
    """Add a platform to a user's owned platforms list, if supported."""
    if platform_name.lower() not in PLATFORM:
        print(f"Platform ({platform_name}) is not supported by SteamUltraDeluxHDRemix2")
        return None

    sql = """
        INSERT INTO owns_platform (user_uuid, platform_uuid)
        VALUES (
            %s,
            (SELECT platform_uuid FROM platform WHERE platform_name ILIKE %s)
        )
        RETURNING *
    """
    try:
        row = execute_query(sql=sql, params=(user_uuid, f"%{platform_name}%"), fetchone=True)
        return row
    except Exception as e:
        print(f"Error inserting platform: {e}")
        return None

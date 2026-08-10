import psycopg # pyright: ignore[reportMissingImports]
import uuid
from src.db import execute_query

PLATFORM = ["pc", "playstation 5","playstation",  "xbox", "nintendo switch", "xbox series x", "xbox series s", "xbox series x|s"]

def add_platform_to_user(uuid: str, platform_name : str):
    if platform_name.lower() in PLATFORM:
        pass

        sql="""
            INSERT INTO owns_platform (user_uuid, platform_uuid) VALUES (
                %s, (
                    SELECT platform_uuid FROM platform
                    WHERE platform_name ILIKE %s
                )
            )

            RETURNING *
        """

        try:
            row = execute_query(sql=sql, params=(uuid, f"%{platform_name}%",),fetchone=True)
            return row
        except Exception as e:
            print(f"Error inserting platform: {e}")
            return


    else:
        print(f"Platform ({platform_name}) is not supported by SteamUltraDeluxHDRemix2")
        return 



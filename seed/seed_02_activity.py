#!/usr/bin/env python3
import os
import sys
import uuid
import random
import psycopg
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in backend/.env")
    sys.exit(1)

BATCH_SIZE = 500

def generate_uuid():
    return str(uuid.uuid4())

def random_date(start_year=2010, end_year=2024):
    return datetime(start_year,1,1) + timedelta(days=random.randint(0, (datetime(end_year,12,31) - datetime(start_year,1,1)).days))

def triangular_round(low, high, mode):
    """Return a rounded integer from a triangular distribution."""
    return int(round(random.triangular(low, high, mode)))

def main():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()
    print("=== PART 2: User Activity (Optimized) ===")

    # ---- Clear activity tables ----
    print("Clearing old user activity...")
    for t in ['follows', 'owns_platform', 'collection_contains', 'collection', 'user_plays', 'user_owns_game']:
        cur.execute(f"DELETE FROM {t};")
    conn.commit()

    # ---- Fetch base data ----
    print("Fetching base data...")
    cur.execute("SELECT user_uuid FROM \"user\";")
    users = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT game_uuid, array_agg(platform_uuid) FROM game_release GROUP BY game_uuid;")
    game_platforms = {row[0]: row[1] for row in cur.fetchall()}
    cur.execute("SELECT platform_uuid FROM platform;")
    all_platforms = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT game_uuid, array_agg(genre_uuid) FROM game_fits_in_genre GROUP BY game_uuid;")
    game_genres = {row[0]: row[1] for row in cur.fetchall()}

    game_list = list(game_platforms.keys())
    total_users = len(users)
    print(f"Processing {total_users} users...")

    # ---- Track totals for reporting ----
    total_owns_platform = 0
    total_owns_game = 0      # user_owns_game rows
    total_plays = 0
    total_collections = 0
    total_contains = 0
    total_follows = 0

    # ---- Batches for bulk inserts ----
    coll_batch = []
    contains_batch = []
    plays_batch = []
    owns_batch = []
    follows_batch = []

    def flush_batches():
        nonlocal total_collections, total_contains, total_plays, total_owns_game, total_follows, total_owns_platform
        if coll_batch:
            cur.executemany("INSERT INTO collection (collection_uuid, user_uuid, collection_name, num_of_games, total_playtime) VALUES (%s, %s, %s, 0, 0) ON CONFLICT (user_uuid, collection_name) DO NOTHING;", coll_batch)
            total_collections += len(coll_batch)
            coll_batch.clear()
        if contains_batch:
            cur.executemany("INSERT INTO collection_contains (collection_uuid, game_uuid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", contains_batch)
            total_contains += len(contains_batch)
            contains_batch.clear()
        if plays_batch:
            cur.executemany("INSERT INTO user_plays (user_uuid, game_uuid, played_at, time_played) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;", plays_batch)
            total_plays += len(plays_batch)
            plays_batch.clear()
        if owns_batch:
            cur.executemany("INSERT INTO user_owns_game (user_uuid, game_uuid, rating) VALUES (%s, %s, %s) ON CONFLICT (user_uuid, game_uuid) DO NOTHING;", owns_batch)
            total_owns_game += len(owns_batch)
            owns_batch.clear()
        if follows_batch:
            cur.executemany("INSERT INTO follows (follower_user_uuid, followed_user_uuid) VALUES (%s, %s) ON CONFLICT (follower_user_uuid, followed_user_uuid) DO NOTHING;", follows_batch)
            total_follows += len(follows_batch)
            follows_batch.clear()

    # ---- Progress tracking ----
    owns_platform_interval = 1000
    owns_platform_next = owns_platform_interval
    owns_game_interval = 5000
    owns_game_next = owns_game_interval
    plays_interval = 5000
    plays_next = plays_interval
    collections_interval = 1000
    collections_next = collections_interval
    contains_interval = 5000
    contains_next = contains_interval
    follows_interval = 1000
    follows_next = follows_interval

    for idx, u in enumerate(users, 1):
        # ---- Step 1: User Platforms ----
        user_plats = random.sample(all_platforms, random.randint(2, 3))
        for p in user_plats:
            cur.execute("INSERT INTO owns_platform (user_uuid, platform_uuid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (u, p))
            total_owns_platform += 1
            if total_owns_platform >= owns_platform_next:
                print(f"  Progress: Inserted {total_owns_platform} rows into owns_platform.")
                owns_platform_next += owns_platform_interval

        # ---- Step 2: Determine Games Owned Count ----
        num_games_owned = triangular_round(2, 22, 11)

        # ---- Step 3: Determine Preferred Genres based on count ----
        if num_games_owned <= 4:
            preferred_genres = []  # 0
        elif num_games_owned <= 9:
            preferred_genres = random.sample(list(set.union(*[set(game_genres.get(g, [])) for g in game_list if g in game_genres])), min(1, len(game_list)))
        elif num_games_owned <= 16:
            preferred_genres = random.sample(list(set.union(*[set(game_genres.get(g, [])) for g in game_list if g in game_genres])), min(2, len(game_list)))
        else:
            preferred_genres = random.sample(list(set.union(*[set(game_genres.get(g, [])) for g in game_list if g in game_genres])), min(3, len(game_list)))

        # If no preferred genres, select uniformly.
        if not preferred_genres:
            selected_games = random.sample(game_list, min(num_games_owned, len(game_list)))
        else:
            # 65% from preferred genres, 35% random
            num_preferred = int(round(num_games_owned * 0.65))
            num_random = num_games_owned - num_preferred

            # Pick preferred games
            preferred_pool = [g for g in game_list if g in game_genres and any(genre in preferred_genres for genre in game_genres[g])]
            selected_preferred = random.sample(preferred_pool, min(num_preferred, len(preferred_pool)))

            # Pick random games from the rest
            remaining_pool = [g for g in game_list if g not in selected_preferred]
            selected_random = random.sample(remaining_pool, min(num_random, len(remaining_pool)))

            selected_games = selected_preferred + selected_random
            random.shuffle(selected_games)  # mix them up

        # ---- Step 4: Generate Play Sessions ----
        total_playtime_per_game = {}
        for g in selected_games:
            sessions = triangular_round(0, 4, 2)
            playtime_total = 0
            for _ in range(sessions):
                played_at = random_date(2020, 2024)
                minutes = random.randint(10, 300)
                plays_batch.append((u, g, played_at, minutes))
                playtime_total += minutes
            total_playtime_per_game[g] = playtime_total

        # ---- Step 5: Calculate Average Playtime ----
        if selected_games:
            avg_playtime = sum(total_playtime_per_game.values()) / len(selected_games)
        else:
            avg_playtime = 0

        # ---- Step 6: Create Favorites Collection ----
        fav_games = [g for g, time in total_playtime_per_game.items() if time >= avg_playtime]
        if fav_games:
            fav_uuid = generate_uuid()
            coll_batch.append((fav_uuid, u, "Favorites"))
            for g in fav_games:
                contains_batch.append((fav_uuid, g))

        # ---- Step 7: Create Genre Collections ----
        # Group owned games by genre
        genre_groups = {}
        for g in selected_games:
            if g in game_genres:
                for genre_uuid in game_genres[g]:
                    genre_groups.setdefault(genre_uuid, []).append(g)

        # Fetch genre names
        cur.execute("SELECT genre_uuid, genre_name FROM genre;")
        genre_name_map = {row[0]: row[1] for row in cur.fetchall()}

        for genre_uuid, games_in_genre in genre_groups.items():
            if len(games_in_genre) >= 3:
                genre_name = genre_name_map.get(genre_uuid, "Unknown")
                coll_name = f"{genre_name}s"
                coll_uuid = generate_uuid()
                coll_batch.append((coll_uuid, u, coll_name))
                for g in games_in_genre:
                    contains_batch.append((coll_uuid, g))

        # ---- Step 8: Ratings (based on playtime) ----
        for g, playtime in total_playtime_per_game.items():
            if playtime == 0:
                rating = random.randint(1, 2)
            elif playtime < avg_playtime:
                rating = random.randint(2, 4)
            else:
                rating = random.randint(4, 5)
            owns_batch.append((u, g, rating))

        # ---- Step 9: Follows ----
        if total_users > 1:
            num_follows = triangular_round(1, 8, 4)
            others = [x for x in users if x != u]
            for f in random.sample(others, min(num_follows, len(others))):
                follows_batch.append((u, f))

        # ---- Flush batches periodically ----
        if len(coll_batch) >= BATCH_SIZE or len(contains_batch) >= BATCH_SIZE or len(plays_batch) >= BATCH_SIZE or len(owns_batch) >= BATCH_SIZE or len(follows_batch) >= BATCH_SIZE:
            flush_batches()
            conn.commit()

        # ---- Progress Reports ----
        if idx % 100 == 0:
            flush_batches()
            conn.commit()
            print(f"Processed {idx}/{total_users} users...")

    # ---- Final Flush ----
    flush_batches()
    conn.commit()

    # ---- Update collection statistics (num_of_games and total_playtime) ----
    print("Updating collection statistics...")
    cur.execute("""
        UPDATE collection c
        SET
            num_of_games = sub.num_games,
            total_playtime = sub.total_playtime
        FROM (
            SELECT
                cc.collection_uuid,
                COUNT(cc.game_uuid) AS num_games,
                COALESCE(SUM(up.time_played), 0) AS total_playtime
            FROM collection_contains cc
            JOIN collection c2 ON cc.collection_uuid = c2.collection_uuid
            LEFT JOIN user_plays up ON up.user_uuid = c2.user_uuid AND up.game_uuid = cc.game_uuid
            GROUP BY cc.collection_uuid
        ) sub
        WHERE c.collection_uuid = sub.collection_uuid;
    """)
    conn.commit()
    print("Collection statistics updated.")

    # ---- Final Totals ----
    print("\n=== USER ACTIVITY IMPORT COMPLETE ===")
    print(f"Final Statistics:")
    print(f"  owns_platform: {total_owns_platform} rows")
    print(f"  user_owns_game: {total_owns_game} rows")
    print(f"  user_plays: {total_plays} rows")
    print(f"  collection: {total_collections} rows")
    print(f"  collection_contains: {total_contains} rows")
    print(f"  follows: {total_follows} rows")
    print("\nAll data seeded successfully.")
    conn.close()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import os
import sys
import csv
import uuid
import random
import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in backend/.env")
    sys.exit(1)

def generate_uuid():
    return str(uuid.uuid4())

def main():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()
    print("=== PART 1: Static Data (Base + Relationships) ===")

    # ---- Truncate static tables ----
    print("Truncating static tables...")
    for t in ['genre', 'platform', 'contributor', '"user"', 'game', 'game_fits_in_genre', 'develops', 'publishes', 'game_release']:
        cur.execute(f"TRUNCATE TABLE {t} CASCADE;")
    conn.commit()

    # ---- 1. Genres ----
    print("\nAdding genres...")
    genres = ["Action","Adventure","RPG","Strategy","Simulation","Sports","Racing","Fighting","Shooter","Puzzle","Platformer","Horror","Survival","Stealth","Educational","Music","Party","MMO","FPS","TPS","Open World","Sandbox","Battle Royale","Indie","Casual","Arcade","Card Game","Board Game","Trivia"]
    for g in genres:
        cur.execute("INSERT INTO genre (genre_uuid, genre_name) VALUES (%s, %s) ON CONFLICT (genre_name) DO NOTHING;", (generate_uuid(), g))
    conn.commit()
    print(f"  Inserted {len(genres)} genres.")

    # ---- 2. Platforms ----
    print("\nAdding platforms...")
    platforms = ["PC", "PlayStation 5", "Xbox Series X", "Nintendo Switch", "PlayStation 4", "Xbox One", "Mobile"]
    for p in platforms:
        cur.execute("INSERT INTO platform (platform_uuid, platform_name) VALUES (%s, %s) ON CONFLICT (platform_name) DO NOTHING;", (generate_uuid(), p))
    conn.commit()
    print(f"  Inserted {len(platforms)} platforms.")

    # ---- 3. Contributors ----
    print("\nLoading contributors...")
    total_contributors = 0
    for i in range(1, 6):
        path = f"seed/data/contributors_{i}.csv"
        if not os.path.exists(path):
            print(f"  {path} not found, skipping.")
            continue
        print(f"  Processing {path}...")
        count = 0
        with open(path, 'r') as f:
            for row in csv.reader(f):
                if row and row[0].strip():
                    cur.execute("INSERT INTO contributor (contributor_uuid, contributor_name) VALUES (%s, %s) ON CONFLICT (contributor_name) DO NOTHING;", (generate_uuid(), row[0].strip()))
                    count += 1
                    total_contributors += 1
        conn.commit()
        print(f"    Inserted {count} contributors from {path}.")
    print(f"  Total contributors inserted: {total_contributors}")

    # ---- 4. Users ----
    print("\nLoading users...")
    total_users = 0
    for i in range(1, 6):
        path = f"seed/data/users_{i}.csv"
        if not os.path.exists(path):
            print(f"  {path} not found, skipping.")
            continue
        print(f"  Processing {path}...")
        count = 0
        with open(path, 'r') as f:
            for row in csv.reader(f):
                if len(row) >= 5:
                    u, p, fn, ln, em = row[:5]
                    cur.execute("""
                        INSERT INTO \"user\" (user_uuid, username, password, first_name, last_name, email, total_playtime, creation_date, last_access_date)
                        VALUES (%s, %s, %s, %s, %s, %s, 0, CURRENT_DATE, CURRENT_DATE) ON CONFLICT (username) DO NOTHING;
                    """, (generate_uuid(), u, p, fn, ln, em))
                    count += 1
                    total_users += 1
        conn.commit()
        print(f"    Inserted {count} users from {path}.")
    print(f"  Total users inserted: {total_users}")

    # ---- 5. Games ----
    print("\nLoading games...")
    path = "seed/data/games.csv"
    if os.path.exists(path):
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cur.execute("""
                    INSERT INTO game (game_uuid, title, game_description, esrb_rating, num_of_players, total_user_rating)
                    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (title) DO NOTHING;
                """, (generate_uuid(), row['title'].strip(), row['description'].strip(), row['esrb_rating'].strip(), int(row['players']), float(row['rating'])))
                count += 1
                if count % 1000 == 0:
                    print(f"    Progress: {count} games inserted...")
        conn.commit()
        print(f"  Inserted {count} games from games.csv.")
    else:
        print("  games.csv not found – skipping games.")

    # ---- 6. Game-Genre links ----
    print("\nLinking games to genres...")
    cur.execute("SELECT game_uuid, title FROM game;")
    game_map = {row[1]: row[0] for row in cur.fetchall()}
    cur.execute("SELECT genre_uuid, genre_name FROM genre;")
    genre_map = {row[1]: row[0] for row in cur.fetchall()}
    path = "seed/data/game_genres.csv"
    if os.path.exists(path):
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if row['game_title'] in game_map and row['genre_name'] in genre_map:
                    cur.execute("INSERT INTO game_fits_in_genre (game_uuid, genre_uuid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (game_map[row['game_title']], genre_map[row['genre_name']]))
                    count += 1
                    if count % 1000 == 0:
                        print(f"    Progress: {count} links inserted...")
        conn.commit()
        print(f"  Inserted {count} game-genre links.")
    else:
        print("  game_genres.csv not found – skipping links.")

    # ---- 7. Developers & Publishers ----
    print("\nAssigning developers and publishers...")
    cur.execute("SELECT contributor_uuid FROM contributor;")
    all_contributors = [row[0] for row in cur.fetchall()]
    random.shuffle(all_contributors)
    split_point = len(all_contributors) // 2
    dev_pool = all_contributors[:split_point]
    pub_pool = all_contributors[split_point:]

    dev_count = 0
    pub_count = 0
    game_uuids = list(game_map.values())
    total_games = len(game_uuids)

    for idx, g_uuid in enumerate(game_uuids, 1):
        # Developers (1–2)
        devs = random.sample(dev_pool, min(random.randint(1, 2), len(dev_pool)))
        for d in devs:
            cur.execute("INSERT INTO develops (contributor_uuid, game_uuid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (d, g_uuid))
            dev_count += 1
        # Publisher (1)
        pub = random.choice(pub_pool)
        cur.execute("INSERT INTO publishes (contributor_uuid, game_uuid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (pub, g_uuid))
        pub_count += 1

        if idx % 1000 == 0:
            conn.commit()
            print(f"    Progress: {idx}/{total_games} games assigned (dev/pubs).")
    conn.commit()
    print(f"  Inserted {dev_count} develops, {pub_count} publishes.")

    # ---- 8. Game Releases ----
    print("\nGenerating game releases...")
    cur.execute("SELECT platform_uuid FROM platform;")
    platform_list = [row[0] for row in cur.fetchall()]
    release_count = 0
    total_games = len(game_uuids)

    for idx, g_uuid in enumerate(game_uuids, 1):
        for p in random.sample(platform_list, random.randint(2, 3)):
            cur.execute("INSERT INTO game_release (game_uuid, platform_uuid, release_date, price) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;",
                        (g_uuid, p, f"{random.randint(2010,2024)}-{random.randint(1,12)}-{random.randint(1,28)}", round(random.uniform(10,80),2)))
            release_count += 1
        if idx % 1000 == 0:
            conn.commit()
            print(f"    Progress: {idx}/{total_games} games processed for releases.")
    conn.commit()
    print(f"  Inserted {release_count} game releases.")

    print("\n=== STATIC DATA IMPORT COMPLETE ===")
    print(f"Summary:")
    print(f"  Users: {total_users}")
    print(f"  Contributors: {total_contributors}")
    print(f"  Games: {len(game_uuids)}")
    print(f"  Game-Genre links: {count if 'count' in locals() else 0}")
    print(f"  Develops: {dev_count}")
    print(f"  Publishes: {pub_count}")
    print(f"  Game Releases: {release_count}")
    print("\nYou can now run: python seed/seed_02_activity.py")
    conn.close()

if __name__ == "__main__":
    main()
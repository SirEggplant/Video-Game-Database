#!/usr/bin/env python3
"""
Seed script that imports static data (genres, platforms, contributors, users,
games) plus relationship tables (developers, publishers, releases).

NOTE: This script generates synthetic demo data. The `random` module is used
intentionally for data generation, not for any security-sensitive purpose.
A fixed seed is applied for reproducibility.
"""

import csv
import os
import random
import sys
import uuid

import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in backend/.env")
    sys.exit(1)

SEED = 42
DATA_DIR = "seed/data"

GENRES = [
    "Action", "Adventure", "RPG", "Strategy", "Simulation", "Sports",
    "Racing", "Fighting", "Shooter", "Puzzle", "Platformer", "Horror",
    "Survival", "Stealth", "Educational", "Music", "Party", "MMO",
    "FPS", "TPS", "Open World", "Sandbox", "Battle Royale", "Indie",
    "Casual", "Arcade", "Card Game", "Board Game", "Trivia",
]

PLATFORMS = [
    "PC", "PlayStation 5", "Xbox Series X", "Nintendo Switch",
    "PlayStation 4", "Xbox One", "Mobile",
]

TRUNCATE_TABLES = [
    "genre", "platform", "contributor", '"user"', "game",
    "game_fits_in_genre", "develops", "publishes", "game_release",
]


def generate_uuid():
    return str(uuid.uuid4())


# seeding

def truncate_tables(cur):
    print("Truncating static tables...")
    for table in TRUNCATE_TABLES:
        cur.execute(f"TRUNCATE TABLE {table} CASCADE;")


def insert_genres(cur):
    print("\nAdding genres...")
    for name in GENRES:
        cur.execute(
            "INSERT INTO genre (genre_uuid, genre_name) VALUES (%s, %s) "
            "ON CONFLICT (genre_name) DO NOTHING;",
            (generate_uuid(), name),
        )
    print(f"  Inserted {len(GENRES)} genres.")


def insert_platforms(cur):
    print("\nAdding platforms...")
    for name in PLATFORMS:
        cur.execute(
            "INSERT INTO platform (platform_uuid, platform_name) VALUES (%s, %s) "
            "ON CONFLICT (platform_name) DO NOTHING;",
            (generate_uuid(), name),
        )
    print(f"  Inserted {len(PLATFORMS)} platforms.")


def load_contributors(cur):
    print("\nLoading contributors...")
    total = 0
    for i in range(1, 6):
        path = f"{DATA_DIR}/contributors_{i}.csv"
        if not os.path.exists(path):
            print(f"  {path} not found, skipping.")
            continue
        print(f"  Processing {path}...")
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0].strip():
                    cur.execute(
                        "INSERT INTO contributor (contributor_uuid, contributor_name) "
                        "VALUES (%s, %s) ON CONFLICT (contributor_name) DO NOTHING;",
                        (generate_uuid(), row[0].strip()),
                    )
                    count += 1
        print(f"    Inserted {count} contributors from {path}.")
        total += count
    print(f"  Total contributors inserted: {total}")
    return total


def load_users(cur):
    print("\nLoading users...")
    total = 0
    for i in range(1, 6):
        path = f"{DATA_DIR}/users_{i}.csv"
        if not os.path.exists(path):
            print(f"  {path} not found, skipping.")
            continue
        print(f"  Processing {path}...")
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) < 5:
                    continue
                username, password, first_name, last_name, email = row[:5]
                cur.execute(
                    'INSERT INTO "user" '
                    "(user_uuid, username, password, first_name, last_name, "
                    " email, total_playtime, creation_date, last_access_date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, 0, CURRENT_DATE, CURRENT_DATE) "
                    "ON CONFLICT (username) DO NOTHING;",
                    (generate_uuid(), username, password, first_name, last_name, email),
                )
                count += 1
        print(f"    Inserted {count} users from {path}.")
        total += count
    print(f"  Total users inserted: {total}")
    return total


def load_games(cur):
    print("\nLoading games...")
    path = f"{DATA_DIR}/games.csv"
    if not os.path.exists(path):
        print("  games.csv not found – skipping games.")
        return 0

    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cur.execute(
                "INSERT INTO game "
                "(game_uuid, title, game_description, esrb_rating, "
                " num_of_players, total_user_rating) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (title) DO NOTHING;",
                (
                    generate_uuid(),
                    row["title"].strip(),
                    row["description"].strip(),
                    row["esrb_rating"].strip(),
                    int(row["players"]),
                    float(row["rating"]),
                ),
            )
            count += 1
            if count % 1000 == 0:
                print(f"    Progress: {count} games inserted...")
    print(f"  Inserted {count} games from games.csv.")
    return count


def link_game_genres(cur):
    print("\nLinking games to genres...")
    cur.execute("SELECT game_uuid, title FROM game;")
    game_map = {row[1]: row[0] for row in cur.fetchall()}
    cur.execute("SELECT genre_uuid, genre_name FROM genre;")
    genre_map = {row[1]: row[0] for row in cur.fetchall()}

    path = f"{DATA_DIR}/game_genres.csv"
    if not os.path.exists(path):
        print("  game_genres.csv not found – skipping links.")
        return 0

    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = row["game_title"]
            genre = row["genre_name"]
            if title not in game_map or genre not in genre_map:
                continue
            cur.execute(
                "INSERT INTO game_fits_in_genre (game_uuid, genre_uuid) "
                "VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (game_map[title], genre_map[genre]),
            )
            count += 1
            if count % 1000 == 0:
                print(f"    Progress: {count} links inserted...")
    print(f"  Inserted {count} game-genre links.")
    return count


def _split_contributor_pools(cur):
    """Return (dev_pool, pub_pool) split from all contributors."""
    cur.execute("SELECT contributor_uuid FROM contributor;")
    all_contributors = [row[0] for row in cur.fetchall()]
    random.shuffle(all_contributors)  # NOSONAR - demo data only
    split = len(all_contributors) // 2
    return all_contributors[:split], all_contributors[split:]


def _insert_developers(cur, game_uuid, dev_pool):
    """Insert 1–2 developers for one game. Returns the number inserted."""
    num = random.randint(1, 2)  # NOSONAR - demo data only
    devs = random.sample(dev_pool, min(num, len(dev_pool)))  # NOSONAR
    for contributor_uuid in devs:
        cur.execute(
            "INSERT INTO develops (contributor_uuid, game_uuid) "
            "VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (contributor_uuid, game_uuid),
        )
    return len(devs)


def assign_developers_and_publishers(cur):
    print("\nAssigning developers and publishers...")
    dev_pool, pub_pool = _split_contributor_pools(cur)
    if not dev_pool or not pub_pool:
        print("  No contributors available – skipping.")
        return 0, 0

    cur.execute("SELECT game_uuid FROM game;")
    game_uuids = [row[0] for row in cur.fetchall()]
    total_games = len(game_uuids)

    dev_count = 0
    pub_count = 0
    for idx, game_uuid in enumerate(game_uuids, 1):
        dev_count += _insert_developers(cur, game_uuid, dev_pool)

        publisher = random.choice(pub_pool)  # NOSONAR - demo data only
        cur.execute(
            "INSERT INTO publishes (contributor_uuid, game_uuid) "
            "VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (publisher, game_uuid),
        )
        pub_count += 1

        if idx % 1000 == 0:
            cur.commit() if hasattr(cur, "commit") else None
            print(f"    Progress: {idx}/{total_games} games assigned (dev/pubs).")

    print(f"  Inserted {dev_count} develops, {pub_count} publishes.")
    return dev_count, pub_count


def _random_release_date():
    """Return a pseudo-random release date string in YYYY-MM-DD format."""
    year = random.randint(2010, 2024)  # NOSONAR - demo data only
    month = random.randint(1, 12)  # NOSONAR
    day = random.randint(1, 28)  # NOSONAR
    return f"{year}-{month:02d}-{day:02d}"


def _insert_releases_for_game(cur, game_uuid, platform_list):
    """Insert 2–3 platform releases for one game. Returns the count inserted."""
    num_platforms = random.randint(2, 3)  # NOSONAR - demo data only
    platforms = random.sample(platform_list, min(num_platforms, len(platform_list)))  # NOSONAR
    for platform_uuid in platforms:
        price = round(random.uniform(10, 80), 2)  # NOSONAR
        cur.execute(
            "INSERT INTO game_release "
            "(game_uuid, platform_uuid, release_date, price) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;",
            (game_uuid, platform_uuid, _random_release_date(), price),
        )
    return len(platforms)


def generate_releases(cur):
    print("\nGenerating game releases...")
    cur.execute("SELECT platform_uuid FROM platform;")
    platform_list = [row[0] for row in cur.fetchall()]
    if not platform_list:
        print("  No platforms available – skipping.")
        return 0

    cur.execute("SELECT game_uuid FROM game;")
    game_uuids = [row[0] for row in cur.fetchall()]
    total_games = len(game_uuids)

    release_count = 0
    for idx, game_uuid in enumerate(game_uuids, 1):
        release_count += _insert_releases_for_game(cur, game_uuid, platform_list)
        if idx % 1000 == 0:
            print(f"    Progress: {idx}/{total_games} games processed for releases.")

    print(f"  Inserted {release_count} game releases.")
    return release_count


# main

def main():
    random.seed(SEED)

    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()
    print("=== PART 1: Static Data (Base + Relationships) ===")

    truncate_tables(cur)
    conn.commit()

    insert_genres(cur)
    conn.commit()

    insert_platforms(cur)
    conn.commit()

    total_contributors = load_contributors(cur)
    conn.commit()

    total_users = load_users(cur)
    conn.commit()

    total_games = load_games(cur)
    conn.commit()

    total_links = link_game_genres(cur)
    conn.commit()

    dev_count, pub_count = assign_developers_and_publishers(cur)
    conn.commit()

    release_count = generate_releases(cur)
    conn.commit()

    print("\n=== STATIC DATA IMPORT COMPLETE ===")
    print("Summary:")
    print(f"  Users: {total_users}")
    print(f"  Contributors: {total_contributors}")
    print(f"  Games: {total_games}")
    print(f"  Game-Genre links: {total_links}")
    print(f"  Develops: {dev_count}")
    print(f"  Publishes: {pub_count}")
    print(f"  Game Releases: {release_count}")
    print("\nYou can now run: python seed/seed_02_activity.py")

    conn.close()


if __name__ == "__main__":
    main()

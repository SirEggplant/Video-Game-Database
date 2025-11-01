import csv
import os
import sys
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db_Connection import execute_query

def main():
    current_dir = os.path.dirname(__file__)
    
    print(f"Starting game-contributor relationships import...")
    
    print("Loading games from database...")
    game_result = execute_query("SELECT game_uuid, title FROM game", fetchall=True)
    
    if not game_result:
        print("❌ ERROR: No games found in database!")
        print("You need to run import_games_only.py first to import games")
        return
    
    game_uuids = [row[0] for row in game_result]
    print(f"✅ Loaded {len(game_uuids)} games from database")
    
    print("Loading contributors from database...")
    contributors_result = execute_query("SELECT contributor_uuid FROM contributor", fetchall=True)
    
    if not contributors_result:
        print("❌ ERROR: No contributors found in database!")
        print("You need to import contributors first")
        return
    
    contributor_uuids = [row[0] for row in contributors_result]
    print(f"✅ Loaded {len(contributor_uuids)} contributors from database")
    
    print("Loading platforms from database...")
    platforms_result = execute_query("SELECT platform_uuid FROM platform", fetchall=True)
    
    if not platforms_result:
        print("❌ ERROR: No platforms found in database!")
        print("You need to import platforms first")
        return
    
    platform_uuids = [row[0] for row in platforms_result]
    print(f"✅ Loaded {len(platform_uuids)} platforms from database")
    
    print("Linking games to random contributors...")
    
    develops_relationships = 0
    publishes_relationships = 0
    
    for game_uuid in game_uuids:
        num_developers = random.randint(1, 2)
        developers = random.sample(contributor_uuids, num_developers)
        
        for dev_uuid in developers:
            execute_query(
                "INSERT INTO develops (contributor_uuid, game_uuid) VALUES (%s, %s)",
                (dev_uuid, game_uuid)
            )
            develops_relationships += 1
        
        publisher_uuid = random.choice(contributor_uuids)
        execute_query(
            "INSERT INTO publishes (contributor_uuid, game_uuid) VALUES (%s, %s)",
            (publisher_uuid, game_uuid)
        )
        publishes_relationships += 1
        
        if develops_relationships % 100 == 0:
            print(f"Processed {develops_relationships} developer relationships...")
    
    print(f"✅ Developer relationships created: {develops_relationships}")
    print(f"✅ Publisher relationships created: {publishes_relationships}")
    
    print("Creating game releases on platforms...")
    
    game_releases = 0
    
    for game_uuid in game_uuids:
        num_platforms = random.randint(2, 3)
        selected_platforms = random.sample(platform_uuids, num_platforms)
        
        for platform_uuid in selected_platforms:
            price = round(random.uniform(10.00, 79.99), 2)
            release_year = random.randint(2010, 2024)
            release_month = random.randint(1, 12)
            release_day = random.randint(1, 28) 
            release_date = f"{release_year}-{release_month:02d}-{release_day:02d}"
            
            execute_query(
                "INSERT INTO game_release (game_uuid, platform_uuid, price, release_date) VALUES (%s, %s, %s, %s)",
                (game_uuid, platform_uuid, price, release_date)
            )
            game_releases += 1
        
        if game_releases % 200 == 0:
            print(f"Processed {game_releases} game releases...")
    
    print(f"✅ Game releases created: {game_releases}")
    
    print(f"\n=== CONTRIBUTOR RELATIONSHIPS IMPORT COMPLETE ===")
    print(f"Developer relationships: {develops_relationships}")
    print(f"Publisher relationships: {publishes_relationships}")
    print(f"Game releases: {game_releases}")

if __name__ == "__main__":
    main()
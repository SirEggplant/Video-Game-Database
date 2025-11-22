import os
import sys
import random
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db_Connection import execute_query

def generate_collections():
    users_with_games = execute_query("""
        SELECT DISTINCT user_uuid FROM user_owns_game 
    """, fetchall=True)
    
    if not users_with_games:
        print("❌ No users with owned games found.")
        return
    
    print(f"Generating collections for {len(users_with_games)} users...")
    
    collection_names = [
        "Favorites", "Backlog", "Completed", "Currently Playing", 
        "Multiplayer", "Single Player", "RPG Collection", "Action Games",
        "Indie Gems", "Classics", "2024 Games", "All-Time Best",
        "Quick Plays", "Weekend Warriors", "Chill Games", "Challenge Mode"
    ]
    
    for i, user_row in enumerate(users_with_games):
        user_uuid = user_row[0]
        
        user_games = execute_query("""
            SELECT uog.game_uuid, g.title, 
                   COALESCE(SUM(up.time_played), 0) as total_playtime
            FROM user_owns_game uog
            JOIN game g ON uog.game_uuid = g.game_uuid
            LEFT JOIN user_plays up ON uog.user_uuid = up.user_uuid AND uog.game_uuid = up.game_uuid
            WHERE uog.user_uuid = %s
            GROUP BY uog.game_uuid, g.title
        """, (user_uuid,), fetchall=True)
        
        if not user_games:
            continue
        
        num_collections = random.randint(1, 3)
        selected_collections = random.sample(collection_names, num_collections)
        
        for collection_name in selected_collections:

            collection_uuid = str(uuid.uuid4())
            
            execute_query("""
                INSERT INTO collection (collection_uuid, user_uuid, collection_name, num_of_games, total_play_time)
                VALUES (%s, %s, %s, 0, 0)
            """, (collection_uuid, user_uuid, collection_name))

            num_games_to_add = random.randint(1, min(8, len(user_games)))
        
            games_with_weights = []
            for game in user_games:
                game_uuid, title, playtime = game

                weight = 1 + (playtime / 60)
                games_with_weights.append((game_uuid, weight))
            
            game_uuids = [game[0] for game in games_with_weights]
            weights = [game[1] for game in games_with_weights]
            
            selected_games = random.choices(game_uuids, weights=weights, k=num_games_to_add)
            
            for game_uuid in selected_games:
                execute_query("""
                    INSERT INTO collection_contains (collection_uuid, game_uuid)
                    VALUES (%s, %s)
                """, (collection_uuid, game_uuid))
            
            execute_query("""
                UPDATE collection 
                SET num_of_games = %s 
                WHERE collection_uuid = %s
            """, (num_games_to_add, collection_uuid))
        
        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1} users...")
    
    print("✅ Collections generation complete!")

if __name__ == "__main__":
    generate_collections()
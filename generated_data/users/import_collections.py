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
        
        # Get user's owned games
        user_games = execute_query("""
            SELECT DISTINCT game_uuid FROM user_owns_game 
            WHERE user_uuid = %s
        """, (user_uuid,), fetchall=True)
        
        if not user_games:
            continue
        
        game_uuids = [game[0] for game in user_games]
        
        # Create 1-3 collections
        num_collections = random.randint(1, 3)
        selected_collections = random.sample(collection_names, num_collections)
        
        for collection_name in selected_collections:
            collection_uuid = str(uuid.uuid4())
            
            # Create collection
            result = execute_query("""
                INSERT INTO collection (collection_uuid, user_uuid, collection_name, num_of_games)
                VALUES (%s, %s, %s, 0)
            """, (collection_uuid, user_uuid, collection_name))
            
            if not result:
                print(f"❌ Failed to create collection {collection_name} for user {user_uuid}")
                continue
            
            # Add 1-6 random games to collection
            num_games_to_add = random.randint(1, min(6, len(game_uuids)))
            selected_games = random.sample(game_uuids, num_games_to_add)
            
            games_added_count = 0
            for game_uuid in selected_games:
                try:
                    result = execute_query("""
                        INSERT INTO collection_contains (collection_uuid, game_uuid)
                        VALUES (%s, %s)
                    """, (collection_uuid, game_uuid))
                    
                    if result:
                        games_added_count += 1
                    else:
                        print(f"⚠️ Failed to add game {game_uuid} to collection {collection_uuid}")
                        
                except Exception as e:
                    print(f"❌ Error adding game to collection: {str(e)}")
            
            # Update game count
            execute_query("""
                UPDATE collection 
                SET num_of_games = %s 
                WHERE collection_uuid = %s
            """, (games_added_count, collection_uuid))
            
            print(f"✅ Created collection '{collection_name}' with {games_added_count} games for user")
        
        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1} users...")
    
    print("✅ Collections generation complete!")

if __name__ == "__main__":
    generate_collections()
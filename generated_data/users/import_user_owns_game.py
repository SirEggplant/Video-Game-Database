import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db_Connection import execute_query
import random

def generate_ownerships():
    # Get first 2500 user UUIDs - CORRECT COLUMN NAME
    users = execute_query("SELECT user_uuid FROM \"user\" LIMIT 2500", fetchall=True)
    # Get all game UUIDs
    games = execute_query("SELECT game_uuid FROM game", fetchall=True)
    
    # Check if queries returned results
    if not users:
        print("❌ No users found in database")
        return
    if not games:
        print("❌ No games found in database")
        return
    
    print(f"Generating ownerships for {len(users)} users and {len(games)} games...")
    
    for i, user in enumerate(users):
        user_uuid = user[0]
        # Each user owns 5-20 random games
        num_games = random.randint(5, 20)
        owned_games = random.sample(games, num_games)
        
        for game in owned_games:
            game_uuid = game[0]
            # Only integer ratings: 1, 2, 3, 4, or 5
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.15, 0.3, 0.35, 0.1])[0]
            
            try:
                execute_query("""
                    INSERT INTO user_owns_game (user_uuid, game_uuid, rating)
                    VALUES (%s, %s, %s)
                """, (user_uuid, game_uuid, rating))
            except Exception as e:
                print(f"Error inserting ownership: {e}")
                continue
        
        if (i + 1) % 100 == 0:  # Progress indicator
            print(f"Processed {i + 1} users...")
    
    print("✅ User-game ownership generation complete!")

# Run the function
if __name__ == "__main__":
    generate_ownerships()
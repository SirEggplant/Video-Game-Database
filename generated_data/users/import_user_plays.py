import os
import sys
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db_Connection import execute_query

def generate_user_plays():
    users_with_games = execute_query("""
        SELECT DISTINCT user_uuid FROM user_owns_game 
    """, fetchall=True)
    
    if not users_with_games:
        print("❌ No users with owned games found. Run user_owns_game generation first.")
        return
    
    print(f"Generating play sessions for {len(users_with_games)} users...")
    
    for i, user_row in enumerate(users_with_games):
        user_uuid = user_row[0]

        owned_games = execute_query("""
            SELECT game_uuid FROM user_owns_game WHERE user_uuid = %s
        """, (user_uuid,), fetchall=True)
        
        if not owned_games:
            continue
            
        total_sessions = random.randint(20, 100)
        
        for session in range(total_sessions):
            game_uuid = random.choice(owned_games)[0]
            
            days_ago = random.randint(1, 365)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            played_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

            time_played = random.choices(
                [random.randint(15, 45), random.randint(46, 120), random.randint(121, 240)],
                weights=[0.6, 0.3, 0.1]
            )[0]
            
            try:
                execute_query("""
                    INSERT INTO user_plays (user_uuid, game_uuid, played_at, time_played)
                    VALUES (%s, %s, %s, %s)
                """, (user_uuid, game_uuid, played_at, time_played))
            except Exception as e:
                print(f"Error inserting play session: {e}")
                continue
        
        if (i + 1) % 50 == 0: 
            print(f"Processed {i + 1} users...")
    
    print("✅ User play sessions generation complete!")

if __name__ == "__main__":
    generate_user_plays()
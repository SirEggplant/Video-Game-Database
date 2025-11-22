import os
import sys
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db_Connection import execute_query

def generate_follows():
    users = execute_query("SELECT user_uuid FROM \"user\" LIMIT 2500", fetchall=True)
    
    if not users:
        print("❌ No users found in database")
        return
    
    print(f"Generating follow relationships for {len(users)} users...")
    
    user_uuids = [user[0] for user in users]
    
    for i, follower_uuid in enumerate(user_uuids):
        num_follows = random.randint(1, 10)
    
        other_users = [uuid for uuid in user_uuids if uuid != follower_uuid]
        followed_users = random.sample(other_users, min(num_follows, len(other_users)))
        
        for followed_uuid in followed_users:
            try:
                execute_query("""
                    INSERT INTO follows (follower_user_uuid, followed_user_uuid)
                    VALUES (%s, %s)
                """, (follower_uuid, followed_uuid))
            except Exception as e:
                if "duplicate" not in str(e).lower():
                    print(f"Error inserting follow: {e}")
                continue
        
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} users...")
    
    print("✅ Follow relationships generation complete!")
    
    total_follows = execute_query("SELECT COUNT(*) FROM follows", fetchone=True)[0]
    avg_follows = execute_query("SELECT AVG(follow_count) FROM (SELECT follower_user_uuid, COUNT(*) as follow_count FROM follows GROUP BY follower_user_uuid) as counts", fetchone=True)[0]
    
    print(f"Total follow relationships: {total_follows}")
    print(f"Average follows per user: {avg_follows:.1f}")

if __name__ == "__main__":
    generate_follows()
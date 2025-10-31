import uuid
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db_Connection import execute_query

def main():
    print("Starting genre import...")
    
    # First, check the actual table structure
    print("Checking genre table structure...")
    structure = execute_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'genre'
        ORDER BY ordinal_position;
    """, fetchall=True)
    
    if structure:
        print("Genre table structure:")
        for col in structure:
            print(f"  - {col[0]} ({col[1]})")
    else:
        print("Genre table doesn't exist or can't be queried")
    
    # Create genres table if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS genre (
        genre_UUID UUID PRIMARY KEY,
        genre_name VARCHAR(255) NOT NULL UNIQUE
    );
    """
    execute_query(create_table_sql)
    print("✅ Genre table created/verified")
    
    # Common video game genres
    common_genres = [
        "Action", "Adventure", "Role-Playing", "Strategy", "Simulation",
        "Sports", "Racing", "Fighting", "Shooter", "Puzzle", "Platformer",
        "Horror", "Survival", "Stealth", "Educational", "Music", "Party",
        "MMO", "RPG", "FPS", "TPS", "Open World", "Sandbox", "Battle Royale",
        "Indie", "Casual", "Arcade", "Card Game", "Board Game", "Trivia"
    ]
    
    success_count = 0
    fail_count = 0
    
    for genre_name in common_genres:
        genre_uuid = str(uuid.uuid4())
        
        result = execute_query(
            "INSERT INTO genre (genre_UUID, genre_name) VALUES (%s, %s)",  # ← CHANGED to genre_name
            (genre_uuid, genre_name)
        )
        
        if result is not None:
            print(f"✅ Added: {genre_name}")
            success_count += 1
        else:
            print(f"❌ Failed: {genre_name}")
            fail_count += 1
    
    print(f"\n=== GENRE IMPORT COMPLETE ===")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total genres: {success_count + fail_count}")

if __name__ == "__main__":
    main()
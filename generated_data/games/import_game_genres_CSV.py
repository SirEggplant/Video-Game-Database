import csv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db_Connection import execute_query

def main():
    current_dir = os.path.dirname(__file__)
    genres_csv_path = os.path.join(current_dir, "game_genres.csv")
    
    print(f"Starting game-genre relationships import...")
    print(f"Genre relationships from: {genres_csv_path}")
    
    if not os.path.exists(genres_csv_path):
        print(f"❌ ERROR: File not found: {genres_csv_path}")
        print("You need to have game_genres.csv in the same directory")
        return
    
    print("Loading games from database...")
    game_mapping = {}
    game_result = execute_query("SELECT game_uuid, title FROM game", fetchall=True)
    
    if not game_result:
        print("❌ ERROR: No games found in database!")
        print("You need to run import_games_only.py first to import games")
        return
    
    for game_row in game_result:
        game_mapping[game_row[1]] = game_row[0] 
    
    print(f"✅ Loaded {len(game_mapping)} games from database")
    
    genre_relationships = 0
    genre_uuid_cache = {}
    
    genre_result = execute_query("SELECT genre_uuid, genre_name FROM genre", fetchall=True)
    for genre_row in genre_result:
        genre_uuid_cache[genre_row[1]] = genre_row[0]
    
    print(f"✅ Loaded {len(genre_uuid_cache)} genres from database")
    
    missing_games = set()
    missing_genres = set()
    
    with open(genres_csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if row:
                game_title = row['game_title'].strip()
                genre_name = row['genre_name'].strip()
                
                if game_title in game_mapping and genre_name in genre_uuid_cache:
                    game_uuid = game_mapping[game_title]
                    genre_uuid = genre_uuid_cache[genre_name]
                    
                    execute_query(
                        "INSERT INTO game_fits_in_genre (game_uuid, genre_uuid) VALUES (%s, %s)",
                        (game_uuid, genre_uuid)
                    )
                    
                    genre_relationships += 1
                    
                    if genre_relationships % 200 == 0:
                        print(f"Processed {genre_relationships} genre relationships...")
                else:
                    if game_title not in game_mapping:
                        missing_games.add(game_title)
                    if genre_name not in genre_uuid_cache:
                        missing_genres.add(genre_name)
    
    print(f"✅ Genre relationships created: {genre_relationships}")
    
    if missing_games:
        print(f"⚠️  {len(missing_games)} games from CSV not found in database (first 10):")
        for game in list(missing_games)[:10]:
            print(f"   - '{game}'")
    
    if missing_genres:
        print(f"⚠️  {len(missing_genres)} genres from CSV not found in database:")
        for genre in missing_genres:
            print(f"   - '{genre}'")
        print("\nAvailable genres in database:")
        for genre_name in sorted(genre_uuid_cache.keys()):
            print(f"   - '{genre_name}'")
    
    print(f"\n=== GENRE RELATIONSHIPS IMPORT COMPLETE ===")
    print(f"Genre relationships created: {genre_relationships}")

if __name__ == "__main__":
    main()
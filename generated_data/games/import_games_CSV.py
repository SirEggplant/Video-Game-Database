import csv
import uuid
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db_Connection import execute_query

def main():
    current_dir = os.path.dirname(__file__)
    games_csv_path = os.path.join(current_dir, "games.csv")
    
    print(f"Starting game import from: {games_csv_path}")
    
    game_mapping = {} 
    games_imported = 0
    
    with open(games_csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if row:
                title = row['title'].strip()
                description = row['description'].strip()
                esrb_rating = row['esrb_rating'].strip()
                players = int(row['players'])
                rating = float(row['rating'])
                
                if title:
                    game_uuid = str(uuid.uuid4())
                    
                    sql = """
                        INSERT INTO game 
                        (game_uuid, title, game_description, esrb_rating, num_of_players, total_user_rating)
                        VALUES (%s, %s, %s, %s::esrb, %s, %s)
                    """
                    
                    execute_query(
                        sql,
                        (game_uuid, title, description, esrb_rating, players, rating)
                    )
                    
                    game_mapping[title] = game_uuid
                    games_imported += 1
                    
                    if games_imported % 100 == 0:
                        print(f"Processed {games_imported} games...")
    
    print(f"✅ Games imported: {games_imported}")
    
    mapping_file = os.path.join(current_dir, "game_mapping.csv")
    with open(mapping_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'game_uuid'])
        for title, game_uuid in game_mapping.items():
            writer.writerow([title, game_uuid])
    
    print(f"✅ Game mapping saved to: {mapping_file}")
    
    print(f"\n=== GAMES IMPORT COMPLETE ===")
    print(f"Games imported: {games_imported}")
    
    game_count = execute_query("SELECT COUNT(*) FROM game", fetchone=True)
    if game_count:
        print(f"Total games in database: {game_count[0]}")

if __name__ == "__main__":
    main()
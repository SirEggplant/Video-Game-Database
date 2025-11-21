import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db_Connection import execute_query

def check_genres():
    print("=== CHECKING GENRES IN DATABASE ===")
    
    count = execute_query("SELECT COUNT(*) FROM genre;", fetchone=True)
    print(f"Total genres in database: {count[0]}")
    
    genres = execute_query("SELECT genre_UUID, genre_name FROM genre ORDER BY genre_name;", fetchall=True)
    print("\nAll genres:")
    for genre in genres:
        print(f"  - {genre[1]}")
    
    test_genre = "RPG"
    search_result = execute_query(
        "SELECT * FROM genre WHERE genre_name ILIKE %s;", 
        (f"%{test_genre}%",), 
        fetchone=True
    )
    if search_result:
        print(f"\n✅ Can search for genre '{test_genre}': {search_result}")
    else:
        print(f"\n❌ Cannot find genre '{test_genre}'")

if __name__ == "__main__":
    check_genres()
import csv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db_Connection import execute_query

def main():
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "user_platforms2.csv")
    
    print(f"Starting import from: {csv_path}")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_platforms (
        user_uuid UUID REFERENCES contributors(contributor_UUID),
        platform_uuid UUID,
        PRIMARY KEY (user_uuid, platform_uuid)
    );
    """
    execute_query(create_table_sql)
    print("✅ user_platforms table created/verified")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        success_count = 0
        second_count = 0
        duplicate_count = 0
        fail_count = 0
        
        for i, row in enumerate(reader):
            if row and len(row) >= 2:
                user_uuid = row[0].strip()
                platform_uuid = row[1].strip()
                
                if user_uuid and platform_uuid:
                    try:
                        result = execute_query(
                            "INSERT INTO owns_platform (user_uuid, platform_uuid) VALUES (%s, %s)",
                            (user_uuid, platform_uuid)
                        )
                        
                        if result:
                            print(f"✅ Added: User {user_uuid} -> Platform {platform_uuid}")
                            success_count += 1
                        else:
                            print(f"✅ Added: User {user_uuid} -> Platform {platform_uuid}")
                            second_count += 1
                            
                    except Exception as e:
                        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                            print(f"⚠️  Duplicate skipped: User {user_uuid} -> Platform {platform_uuid}")
                            duplicate_count += 1
                        else:
                            print(f"❌ Error: User {user_uuid} -> Platform {platform_uuid}: {str(e)}")
                            fail_count += 1
                else:
                    print(f"⚠️  Skipped invalid row {i+1}: {row}")
                    fail_count += 1
            else:
                print(f"⚠️  Skipped malformed row {i+1}: {row}")
                fail_count += 1
        
        print(f"\n=== IMPORT COMPLETE ===")
        print(f"Successful: {success_count}")
        print(f"Second Count: {second_count}")
        print(f"Failed: {fail_count}")
        print(f"Duplicates skipped: {duplicate_count}")
        print(f"Total assignments: {success_count}")

if __name__ == "__main__":
    main()
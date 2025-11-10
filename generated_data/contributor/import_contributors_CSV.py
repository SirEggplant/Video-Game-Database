import csv
import uuid
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db_Connection import execute_query

def main():
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "MOCK_DATA (4).csv")
    
    print(f"Starting import from: {csv_path}")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS contributors (
        contributor_UUID UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    """
    execute_query(create_table_sql)
    print("✅ Table created/verified")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        
        total_count = 0
        
        for row in reader:
            if row:
                company_name = row[0].strip()
                if company_name:
                    company_uuid = str(uuid.uuid4())
                    total_count += 1
                    
                    execute_query(
                        "INSERT INTO contributors (contributor_UUID, name) VALUES (%s, %s)",
                        (company_uuid, company_name)
                    )
                    
                    if total_count % 100 == 0:
                        print(f"Processed {total_count} records...")
        
        print(f"\n=== IMPORT COMPLETE ===")
        print(f"Total records processed: {total_count}")
        
        count_result = execute_query("SELECT COUNT(*) FROM contributors;", fetchone=True)
        if count_result:
            print(f"Total records in database: {count_result[0]}")

if __name__ == "__main__":
    main()

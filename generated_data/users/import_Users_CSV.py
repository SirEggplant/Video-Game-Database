import csv
import uuid
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db_Connection import execute_query

def main():
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "MOCK_DATA.csv")
    
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
        
        success_count = 0
        fail_count = 0
        
        for i, row in enumerate(reader):
            if row:
                company_name = row[0].strip()
                if company_name:
                    company_uuid = str(uuid.uuid4())
                    
                    result = execute_query(
                        "INSERT INTO contributors (contributor_UUID, name) VALUES (%s, %s)",
                        (company_uuid, company_name)
                    )
                    
                    if result:
                        print(f"✅ Added: {company_name}")
                        success_count += 1
                    else:
                        print(f"❌ Failed: {company_name} (may already exist)")
                        fail_count += 1
        
        print(f"\n=== IMPORT COMPLETE ===")
        print(f"Successful: {success_count}")
        print(f"Failed: {fail_count}")

if __name__ == "__main__":
    main()

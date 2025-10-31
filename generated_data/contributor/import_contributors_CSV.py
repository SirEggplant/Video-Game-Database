import csv
import uuid
import psycopg2  # pyright: ignore[reportMissingImports]

def main():
    password = input("Password: ")
    conn_params = {
        "dbname": "p320_46",
        "user": "jnd6300",
        "password": password,
        "host": "127.0.0.1",
        "port": 5432
    }

    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            with open('MOCK_DATA.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    # Assuming company_name is in the first column of each row
                    company_name = row[0]
                    company_uuid = str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO contributors (contributor_UUID, contributor_name) VALUES (%s, %s)",
                        (company_uuid, company_name)
                    )
        conn.commit()

if __name__ == "__main__":
    main()

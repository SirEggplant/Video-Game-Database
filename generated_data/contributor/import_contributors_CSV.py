import csv
import uuid
import psycopg # pyright: ignore[reportMissingImports]

def main():
    password = input("Password: ")
    with psycopg.connect("dbname=p320_46 user=jnd6300 password=" + password + " host=127.0.0.1") as conn:
        with conn.cursor() as cur:
            with open('MOCK_DATA.csv', 'r') as f:
                for line in f:
                    company_name = line
                    company_uuid = str(uuid.uuid4())
                    cur.execute("INSERT INTO contributors (contributor_UUID, contributor_name) VALUES (%s, %s)", (company_uuid, company_name))
        conn.commit()


if __name__ == "__main__":
    main()
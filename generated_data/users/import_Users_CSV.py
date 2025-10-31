import csv

from authentication import (
    register
)

def main():
    with open("MOCK_DATA.csv", 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            register(row)

if __name__ == "__main__":
    main()
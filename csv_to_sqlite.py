import csv
import sqlite3
import sys
import os

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <database file> <csv file>")
        sys.exit(1)
    
    db_file = sys.argv[1]
    csv_file = sys.argv[2]
    
    # Use the CSV file's base name (without extension) as the table name.
    table_name = os.path.splitext(os.path.basename(csv_file))[0]
    
    # Read CSV data
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("Error: CSV file is empty.")
            sys.exit(1)
        rows = list(reader)
    
    # Connect to SQLite and create table
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    # Create table: assume every column is TEXT.
    columns_def = ', '.join([f'"{col}" TEXT' for col in header])
    cur.execute(f"CREATE TABLE {table_name} ({columns_def})")
    
    placeholders = ', '.join(['?'] * len(header))
    cur.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
    
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    main()

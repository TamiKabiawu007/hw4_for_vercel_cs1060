#!/usr/bin/env python3
import argparse
import csv
import os
import sqlite3
import sys

def convert_csv_to_sqlite(db_path, csv_path):
    # Derive table name from CSV filename (without extension)
    table_name = os.path.splitext(os.path.basename(csv_path))[0]

    # Open the CSV and extract header and rows
    with open(csv_path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        try:
            header = next(reader)
        except StopIteration:
            sys.exit("Error: CSV file is empty.")
        records = list(reader)

    # Connect to the SQLite database using a context manager
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Remove any existing table with the same name
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        # Create table with each column as TEXT
        columns = ', '.join([f'"{col}" TEXT' for col in header])
        create_table = f"CREATE TABLE {table_name} ({columns})"
        cursor.execute(create_table)
        # Insert records into the table
        placeholders = ', '.join('?' for _ in header)
        insert_stmt = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cursor.executemany(insert_stmt, records)
        conn.commit()

def main():
    parser = argparse.ArgumentParser(description="Import a CSV file into a SQLite database.")
    parser.add_argument("database", help="Output SQLite database file (e.g., data.db)")
    parser.add_argument("csvfile", help="Input CSV file with a header row")
    args = parser.parse_args()

    convert_csv_to_sqlite(args.database, args.csvfile)

if __name__ == '__main__':
    main()

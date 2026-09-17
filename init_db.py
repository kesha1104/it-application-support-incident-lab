import sqlite3
from pathlib import Path

project_directory = Path(__file__).resolve().parent
database_path = project_directory / "tickets.db"
schema_path = project_directory / "schema.sql"

connection = sqlite3.connect(database_path)

with open(schema_path, encoding="utf-8") as schema_file:
    connection.executescript(schema_file.read())

connection.close()

print("Ticket database created successfully.")
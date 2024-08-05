"""
Script to reset the database schema.
"""

import sqlite3


def reset_database(db_file="data/songs.db", schema_file="db/schema.sql"):
    """
    Reset the database by dropping and recreating the songs table.

    Args:
        db_file (str): Path to the database file.
        schema_file (str): Path to the schema file.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS songs")
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = f.read()
    cursor.executescript(schema)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    reset_database()

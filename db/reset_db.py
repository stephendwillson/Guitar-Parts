"""
Script to reset the database schema.
"""

import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import (  # noqa: E402 - Import not at top of file
    get_resource_path,
    get_default_db_path,
)


def reset_database(db_file=None, schema_file="db/schema.sql"):
    """
    Reset the database by dropping and recreating the songs table.

    Args:
        db_file (str): Path to the database file.
        schema_file (str): Path to the schema file.
    """
    if db_file is None:
        db_file = get_default_db_path()

    db_file_path = get_resource_path(db_file)
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS songs")

    schema_path = get_resource_path(schema_file)
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    cursor.executescript(schema)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Make super duper sure that the user wants to reset the database
    if os.getenv("ALLOW_DB_RESET") == "true":
        reset_database()
    else:
        print(
            "Database reset is not allowed. Set ALLOW_DB_RESET environment variable "
            "to 'true' to enable."
        )

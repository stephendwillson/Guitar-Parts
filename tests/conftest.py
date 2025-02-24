import os
import sys
import pytest

# Make sure project root dir is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.db import initialize_db  # noqa: E402 - Import not at top of file


@pytest.fixture
def db_cursor():
    """Create a test database cursor"""
    conn, cursor = initialize_db(":memory:")
    yield cursor
    conn.close()

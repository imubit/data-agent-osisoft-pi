"""
    Dummy conftest.py for daconnect_osisoft_pi.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest

from daconnect_osisoft_pi.connector import OsisoftPiConnector

# TEST_SERVER_NAME = 'DATA-ANALYSIS-W'
# TEST_SERVER_VERSION = '3.4.395.80'

TEST_SERVER_NAME = "10.142.0.121"
TEST_SERVER_VERSION = "3.4.445.688"

PAGE_SIZE = 1000


@pytest.fixture
def target_conn():
    conn = OsisoftPiConnector(server_name=TEST_SERVER_NAME, page_size=PAGE_SIZE)
    conn.connect()
    yield conn
    conn.disconnect()

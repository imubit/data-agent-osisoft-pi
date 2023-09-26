import os

import pytest

from data_agent_osisoft_pi.connector import OsisoftPiConnector

TEST_SERVER_NAME = os.environ.get("PI_SERVER", "127.0.0.1")
TEST_SERVER_VERSION = "3.4.445.688"

PAGE_SIZE = 1000


@pytest.fixture
def target_conn():
    conn = OsisoftPiConnector(server_name=TEST_SERVER_NAME, page_size=PAGE_SIZE)
    conn.connect()
    yield conn
    conn.disconnect()

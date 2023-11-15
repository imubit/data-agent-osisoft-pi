import numpy as np
from conftest import TEST_SERVER_NAME, TEST_SERVER_VERSION

from data_agent_osisoft_pi.connector import OsisoftPiConnector


def test_list_registered_targets():
    targets = OsisoftPiConnector.list_registered_targets()
    for t in targets:
        if t["Name"] == TEST_SERVER_NAME:
            return

    assert False


def test_sanity():
    conn = OsisoftPiConnector(server_name=TEST_SERVER_NAME)
    assert not conn.connected
    conn.connect()
    assert conn.connected

    assert conn.TYPE == "osisoft-pi"

    info = conn.connection_info()
    assert info["ServerName"] == TEST_SERVER_NAME
    assert info["Version"] == TEST_SERVER_VERSION
    assert info["Description"] == ""

    conn.disconnect()
    assert not conn.connected


def test_list_tags_filter(target_conn):
    tags = target_conn.list_tags()
    assert "SINUSOID" in tags

    tags = target_conn.list_tags(filter="SINUSOIDU")
    assert "SINUSOIDU" in tags
    assert len(tags) == 1

    tags = target_conn.list_tags(filter="SINUSOID*")
    assert "SINUSOIDU" in tags
    assert len(tags) == 2

    tags = target_conn.list_tags(filter="SINUSOID*", max_results=1)
    assert len(tags) == 1

    tags = target_conn.list_tags(filter="SINUSOID*", include_attributes=True)
    assert tags["SINUSOID"]["pointtype"] == np.float32


def test_list_tags_list(target_conn):
    tags = target_conn.list_tags(filter=["SINUSOID", "SINUSOIDU"], max_results=6)
    assert len(tags) == 2

    tags = target_conn.list_tags(
        filter=["SINUSOID", "SINUSOIDU", "NON_EXISTING"], max_results=6
    )
    assert len(tags) == 2


def test_read_tag_values_period_interpolated(target_conn):
    df = target_conn.read_tag_values_period(
        ["sinusoidu"],
        first_timestamp="*-50m",
        last_timestamp="*",
        time_frequency="1 minute",
    )
    assert len(df) == 51
    assert list(df.columns) == ["SINUSOIDU"]

    df = target_conn.read_tag_values_period(
        ["sinusoidu"],
        first_timestamp="*-100h",
        last_timestamp="*",
        time_frequency="1 minute",
    )

    assert len(df) == 6000
    assert list(df.columns) == ["SINUSOIDU"]

    df = target_conn.read_tag_values_period(
        ["sinusoidu"],
        first_timestamp="*-100h",
        last_timestamp="*",
        time_frequency="1 minute",
        max_results=10,
    )

    assert len(df) == 10
    assert list(df.columns) == ["SINUSOIDU"]

    df = target_conn.read_tag_values_period(
        ["SINUSOIDU"],
        first_timestamp="2023-07-15 11:37:35.551000",
        last_timestamp="2023-08-14 11:37:35.551000",
        time_frequency="1 minute",
    )

    assert len(df) == 43201
    assert list(df.columns) == ["SINUSOIDU"]

    df = target_conn.read_tag_values_period(
        ["sinusoid", "sinusoidu"],
        first_timestamp="*-100h",
        last_timestamp="*",
        time_frequency="3 minutes",
    )

    assert len(df) == 2000
    assert list(df.columns) == ["SINUSOID", "SINUSOIDU"]


def test_read_tag_values_period_recorded(target_conn):
    df = target_conn.read_tag_values_period(
        ["sinusoid", "sinusoidu"],
        # first_timestamp='*-100h',
        # last_timestamp='*',
        first_timestamp="2019/09/02 00:00:05",
        last_timestamp="2020/09/02 00:00:05",
    )
    assert list(df.columns) == ["SINUSOID", "SINUSOIDU"]

    df = target_conn.read_tag_values_period(
        ["sinusoid", "sinusoidu"],
        first_timestamp="*-200h",
        last_timestamp="*-100h",
    )
    assert list(df.columns) == ["SINUSOID", "SINUSOIDU"]

    df = target_conn.read_tag_values_period(
        ["sinusoid", "sinusoidu"],
        first_timestamp="2020-04-15 12:00:00",
        last_timestamp="2020-05-16 12:00:00",
        max_results=10,
    )
    assert list(df.columns) == ["SINUSOID", "SINUSOIDU"]
    assert len(df) == 10

    df = target_conn.read_tag_values_period(
        ["sinusoid", "sinusoidu"],
        first_timestamp="2020-04-15 12:00:00",
        last_timestamp="2020-12-16 12:00:00",
        max_results=2000,
    )
    assert list(df.columns) == ["SINUSOID", "SINUSOIDU"]
    assert len(df) == 2000


def test_read_tag_attributes(target_conn):
    res = target_conn.read_tag_attributes(
        ["sinusoid", "sinusoidu"], attributes=["tag", "pointtype"]
    )

    assert res == {
        "SINUSOID": {"tag": "SINUSOID", "pointtype": np.float32},
        "SINUSOIDU": {"tag": "SINUSOIDU", "pointtype": np.float32},
    }

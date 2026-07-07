import sqlite3
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.analytics import create_database, QUERIES


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    create_database(c)
    yield c
    c.close()


def test_database_seeded(conn):
    count = conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    assert count == 15


def test_summary_query(conn):
    df = pd.read_sql_query(QUERIES["summary"], conn)
    assert df["total_claims"].iloc[0] == 15
    assert df["total_amount"].iloc[0] > 0
    assert df["flagged_count"].iloc[0] == 5


def test_high_value_claims(conn):
    df = pd.read_sql_query(QUERIES["high_value"], conn)
    assert all(df["amount"] > 500)
    assert len(df) >= 1


def test_monthly_trend(conn):
    df = pd.read_sql_query(QUERIES["monthly_trend"], conn)
    assert len(df) >= 1
    assert "month" in df.columns
    assert "total" in df.columns


def test_top_patients(conn):
    df = pd.read_sql_query(QUERIES["top_patients"], conn)
    assert len(df) <= 5
    amounts = df["total_spent"].tolist()
    assert amounts == sorted(amounts, reverse=True)


def test_flagged_by_state(conn):
    df = pd.read_sql_query(QUERIES["flagged_by_state"], conn)
    assert "state" in df.columns
    assert "flagged_claims" in df.columns

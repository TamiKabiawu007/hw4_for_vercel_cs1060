import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import sqlite3
from api.county_data import app


@pytest.fixture
def test_db():
    # Create an in-memory SQLite database and set up the county_health_rankings table
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE county_health_rankings (
        State TEXT,
        County TEXT,
        State_code TEXT,
        County_code TEXT,
        Year_span TEXT,
        Measure_name TEXT,
        Measure_id TEXT,
        Numerator TEXT,
        Denominator TEXT,
        Raw_value TEXT,
        Confidence_Interval_Lower_Bound TEXT,
        Confidence_Interval_Upper_Bound TEXT,
        Data_Release_Year TEXT,
        fipscode TEXT
    )
    ''')
    # Insert a sample row for Adult obesity
    c.execute('''
    INSERT INTO county_health_rankings VALUES (
        'MA', 'Middlesex County', '25', '17', '2009', 'Adult obesity', '11', '60771.02', '263078', '0.23', '0.22', '0.24', '2012', '25017'
    )
    ''')
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def override_sqlite_connect(monkeypatch, test_db):
    # Override sqlite3.connect to always return the in-memory test_db
    def in_memory_connect(db_path):
        return test_db
    monkeypatch.setattr(sqlite3, 'connect', in_memory_connect)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


def test_valid_request(client):
    # Test valid POST request
    response = client.post("/county_data", json={"zip": "02138", "measure_name": "Adult obesity"})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    expected_keys = {"state", "county", "state_code", "county_code", "year_span", "measure_name", "measure_id", "numerator", "denominator", "raw_value", "confidence_interval_lower_bound", "confidence_interval_upper_bound", "data_release_year", "fipscode"}
    for row in data:
        assert expected_keys == set(row.keys())
        for value in row.values():
            assert isinstance(value, str)


def test_coffee_teapot(client):
    # Test that coffee=teapot returns HTTP 418
    response = client.post("/county_data", json={"coffee": "teapot"})
    assert response.status_code == 418


def test_missing_params(client):
    # Test missing zip
    response = client.post("/county_data", json={"measure_name": "Adult obesity"})
    assert response.status_code == 400
    # Test missing measure_name
    response = client.post("/county_data", json={"zip": "02138"})
    assert response.status_code == 400


def test_no_data(client):
    # Test valid input that returns no data (allowed measure but not in test DB)
    response = client.post("/county_data", json={"zip": "02138", "measure_name": "Uninsured"})
    assert response.status_code == 404


import sqlite3
import pandas as pd

from src.database import publish_customers


def create_customer(city="Hyderabad", age=25, run_id="run_001",
                    processed_at="2026-11-13T10:00:00+00:00"):

    return pd.DataFrame([{
        "customer_id": 101,
        "customer_name": "Ravi",
        "email": "ravi@gmail.com",
        "age": age,
        "city": city,
        "phone_number": "9876543210",
        "run_id": run_id,
        "source_file": "customers.csv",
        "processed_at": processed_at
    }])


def test_first_customer_insert_creates_history(tmp_path):

    db_path = tmp_path / "test_customer.db"

    customer_data = create_customer()

    publish_customers(customer_data, str(db_path))

    with sqlite3.connect(db_path) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT customer_id, city, is_current, effective_to
            FROM customer_history
        """)

        history = cursor.fetchall()

    assert len(history) == 1
    assert history[0][0] == 101
    assert history[0][1] == "Hyderabad"
    assert history[0][2] == 1
    assert history[0][3] is None


def test_customer_update_preserves_previous_version(tmp_path):

    db_path = tmp_path / "test_customer.db"

    # First version
    first_data = create_customer(
        city="Hyderabad",
        age=25,
        processed_at="2026-11-13T10:00:00+00:00"
    )

    publish_customers(first_data, str(db_path))

    # Updated version
    updated_data = create_customer(
        city="Bangalore",
        age=26,
        run_id="run_002",
        processed_at="2026-11-13T11:00:00+00:00"
    )

    publish_customers(updated_data, str(db_path))

    with sqlite3.connect(db_path) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT city, age, is_current, effective_to
            FROM customer_history
            WHERE customer_id = 101
            ORDER BY history_id
        """)

        history = cursor.fetchall()

        cursor.execute("""
            SELECT city, age
            FROM customers
            WHERE customer_id = 101
        """)

        latest_customer = cursor.fetchone()

    assert len(history) == 2

    # Previous version
    assert history[0][0] == "Hyderabad"
    assert history[0][1] == 25
    assert history[0][2] == 0
    assert history[0][3] is not None

    # Current version
    assert history[1][0] == "Bangalore"
    assert history[1][1] == 26
    assert history[1][2] == 1
    assert history[1][3] is None

    # Latest customer table
    assert latest_customer == ("Bangalore", 26)


def test_identical_rerun_does_not_create_history_version(tmp_path):

    db_path = tmp_path / "test_customer.db"

    first_data = create_customer()

    publish_customers(first_data, str(db_path))

    # Same business data, but a different pipeline run
    second_data = create_customer(
        run_id="run_002",
        processed_at="2026-11-13T11:00:00+00:00"
    )

    publish_customers(second_data, str(db_path))

    with sqlite3.connect(db_path) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM customer_history
            WHERE customer_id = 101
        """)

        history_count = cursor.fetchone()[0]

    assert history_count == 1

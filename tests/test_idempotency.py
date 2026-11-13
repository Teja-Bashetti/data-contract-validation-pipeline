
import sqlite3
import pandas as pd

from src.database import publish_customers


def test_publishing_same_customer_twice_does_not_create_duplicates(tmp_path):

    db_path = tmp_path / "test_customer.db"

    # Sample customer data
    customer_data = pd.DataFrame([
        {
            "customer_id": 101,
            "customer_name": "Ravi",
            "email": "ravi@gmail.com",
            "age": 25,
            "city": "Hyderabad",
            "phone_number": "9876543210",
            "run_id": "run_001",
            "source_file": "customers.csv",
            "processed_at": "2026-11-13T10:00:00"
        }
    ])

    # First pipeline run
    publish_customers(customer_data, str(db_path))

    # Second pipeline run with the same customer
    publish_customers(customer_data, str(db_path))

    # Check database records
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM customers")
        total_records = cursor.fetchone()[0]

        cursor.execute(
            "SELECT customer_id FROM customers WHERE customer_id = 101"
        )
        customer = cursor.fetchone()

        assert total_records == 1
        assert customer is not None
        assert customer[0] == 101

    finally:
        connection.close()

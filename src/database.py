
import sqlite3
import os


def publish_customers(df, db_path="data/customer_data.db"):
    """
    Publish validated customer records into SQLite.
    """

    # Create database folder if it does not exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to SQLite database
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        # Create customer table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                phone_number TEXT,
                run_id TEXT,
                source_file TEXT,
                processed_at TEXT
            )
        """)

        # Prepare customer records
        records = []

        for row in df.to_dict(orient="records"):
            records.append((
                row["customer_id"],
                row["customer_name"],
                row["email"],
                int(row["age"]),
                row["city"],
                row.get("phone_number"),
                row.get("run_id"),
                row.get("source_file"),
                row.get("processed_at")
            ))

        # Insert or update records using customer_id
        cursor.executemany("""
            INSERT INTO customers (
                customer_id,
                customer_name,
                email,
                age,
                city,
                phone_number,
                run_id,
                source_file,
                processed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(customer_id) DO UPDATE SET
                customer_name = excluded.customer_name,
                email = excluded.email,
                age = excluded.age,
                city = excluded.city,
                phone_number = excluded.phone_number,
                run_id = excluded.run_id,
                source_file = excluded.source_file,
                processed_at = excluded.processed_at
        """, records)

        connection.commit()

        print("\nCustomer records published to SQLite successfully!")
        print("Records processed:", len(records))
        print("Database:", db_path)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

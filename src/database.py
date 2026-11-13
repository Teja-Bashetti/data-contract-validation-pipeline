
import sqlite3
import os
from datetime import datetime, timezone
import math


def get_timestamp(value=None):
    """
    Return an ISO-8601 timestamp.
    Use the pipeline processed_at value when available.
    """

    if value:
        return value

    return datetime.now(timezone.utc).isoformat()


def clean_value(value):
    """
    Convert missing numeric values such as NaN into None.
    """

    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    return value


def publish_customers(df, db_path="data/customer_data.db"):
    """
    Publish customer records into SQLite.

    customers:
        Stores the latest customer version.

    customer_history:
        Stores all customer versions using SCD Type 2.

    Identical reruns do not create duplicate history records.
    """

    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        # 1. Create current customer table
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

        # 2. Create customer history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                phone_number TEXT,
                effective_from TEXT NOT NULL,
                effective_to TEXT,
                is_current INTEGER NOT NULL,
                run_id TEXT,
                source_file TEXT,
                processed_at TEXT
            )
        """)

        # 3. Backfill existing customers into history.
        # This preserves customers already present before SCD Type 2
        # was introduced.
        cursor.execute("""
            INSERT INTO customer_history (
                customer_id,
                customer_name,
                email,
                age,
                city,
                phone_number,
                effective_from,
                effective_to,
                is_current,
                run_id,
                source_file,
                processed_at
            )
            SELECT
                c.customer_id,
                c.customer_name,
                c.email,
                c.age,
                c.city,
                c.phone_number,
                COALESCE(
                    c.processed_at,
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                NULL,
                1,
                c.run_id,
                c.source_file,
                c.processed_at
            FROM customers c
            WHERE NOT EXISTS (
                SELECT 1
                FROM customer_history h
                WHERE h.customer_id = c.customer_id
                  AND h.is_current = 1
            )
        """)

        # 4. Process incoming customer records
        records = df.to_dict(orient="records")

        for row in records:

            customer_id = clean_value(row["customer_id"])
            customer_name = clean_value(row["customer_name"])
            email = clean_value(row["email"])
            age = int(row["age"])
            city = clean_value(row["city"])
            phone_number = clean_value(row.get("phone_number"))

            run_id = clean_value(row.get("run_id"))
            source_file = clean_value(row.get("source_file"))
            processed_at = clean_value(row.get("processed_at"))

            effective_time = get_timestamp(processed_at)

            # Check whether customer already exists
            cursor.execute("""
                SELECT
                    customer_name,
                    email,
                    age,
                    city,
                    phone_number
                FROM customers
                WHERE customer_id = ?
            """, (customer_id,))

            existing = cursor.fetchone()

            new_business_values = (
                customer_name,
                email,
                age,
                city,
                phone_number
            )

            if existing is None:

                # First-time customer: create initial history version
                cursor.execute("""
                    INSERT INTO customer_history (
                        customer_id,
                        customer_name,
                        email,
                        age,
                        city,
                        phone_number,
                        effective_from,
                        effective_to,
                        is_current,
                        run_id,
                        source_file,
                        processed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 1, ?, ?, ?)
                """, (
                    customer_id,
                    *new_business_values,
                    effective_time,
                    run_id,
                    source_file,
                    processed_at
                ))

            elif tuple(existing) != new_business_values:

                # Business data changed:
                # close the previous current version
                cursor.execute("""
                    UPDATE customer_history
                    SET
                        effective_to = ?,
                        is_current = 0
                    WHERE customer_id = ?
                      AND is_current = 1
                """, (effective_time, customer_id))

                # Insert the new current version
                cursor.execute("""
                    INSERT INTO customer_history (
                        customer_id,
                        customer_name,
                        email,
                        age,
                        city,
                        phone_number,
                        effective_from,
                        effective_to,
                        is_current,
                        run_id,
                        source_file,
                        processed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 1, ?, ?, ?)
                """, (
                    customer_id,
                    *new_business_values,
                    effective_time,
                    run_id,
                    source_file,
                    processed_at
                ))

            # 5. Maintain the latest customer record using UPSERT
            cursor.execute("""
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
            """, (
                customer_id,
                *new_business_values,
                run_id,
                source_file,
                processed_at
            ))

        connection.commit()

        print("\nCustomer records published successfully!")
        print("Records processed:", len(records))
        print("Database:", db_path)
        print("Customer history tracking: Enabled")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

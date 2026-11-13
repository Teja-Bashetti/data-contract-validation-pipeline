
import sqlite3

db_path = "data/customer_data.db"

connection = sqlite3.connect(db_path)

queries = {
    "Total published customers": """
        SELECT COUNT(*) FROM customers
    """,

    "Customers by city": """
        SELECT city, COUNT(*)
        FROM customers
        GROUP BY city
    """,

    "Duplicate customer IDs": """
        SELECT customer_id, COUNT(*)
        FROM customers
        GROUP BY customer_id
        HAVING COUNT(*) > 1
    """
}

try:
    cursor = connection.cursor()

    for title, query in queries.items():
        print(f"\n--- {title} ---")

        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            for row in results:
                print(row)
        else:
            print("No records found.")

finally:
    connection.close()

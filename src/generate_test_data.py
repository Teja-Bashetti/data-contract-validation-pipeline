
import os
import random
import pandas as pd


def generate_customers(number_of_records=100000):

    """
    Generate synthetic customer records for performance testing.
    """

    random.seed(42)

    first_names = [
        "Ravi", "Teja", "Arun", "Priya", "Kiran",
        "Suresh", "Anjali", "Vijay", "Manoj", "Divya"
    ]

    last_names = [
        "Kumar", "Sharma", "Reddy", "Patel", "Verma",
        "Singh", "Rao", "Gupta", "Das", "Naidu"
    ]

    cities = [
        "Hyderabad", "Bangalore", "Chennai",
        "Mumbai", "Delhi", "Pune",
        "Kolkata", "Jaipur", "Lucknow", "Kochi"
    ]

    records = []

    for customer_id in range(1, number_of_records + 1):

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        customer_name = f"{first_name} {last_name}"

        email = f"customer{customer_id}@example.com"

        age = random.randint(18, 100)

        city = random.choice(cities)

        records.append({
            "customer_id": customer_id,
            "customer_name": customer_name,
            "email": email,
            "age": age,
            "city": city
        })

    df = pd.DataFrame(records)

    os.makedirs("data/input", exist_ok=True)

    output_path = "data/input/customers_100k.csv"

    df.to_csv(output_path, index=False)

    print("\n========== DATA GENERATION COMPLETED ==========")

    print("Total records generated:", len(df))

    print("Output file:", output_path)

    print("\nSample records:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    return df


if __name__ == "__main__":

    generate_customers(100000)

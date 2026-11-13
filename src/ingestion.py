
import pandas as pd

def read_customer_csv(file_path):
    """
    Read customer data from a CSV file.
    """
    df = pd.read_csv(file_path)

    print("CSV file loaded successfully!")
    print("\nCustomer data:")
    print(df)

    print("\nDataFrame information:")
    print(df.info())

    return df
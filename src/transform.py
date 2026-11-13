
import pandas as pd


def transform_customer_data(df):
    """
    Clean and standardize validated customer records.
    """

    # Work on a copy so the original data is unchanged
    transformed_df = df.copy()

    # Standardize customer names
    if "customer_name" in transformed_df.columns:
        transformed_df["customer_name"] = (
            transformed_df["customer_name"]
            .str.strip()
            .str.title()
        )

    # Standardize email addresses
    if "email" in transformed_df.columns:
        transformed_df["email"] = (
            transformed_df["email"]
            .str.strip()
            .str.lower()
        )

    # Standardize city names
    if "city" in transformed_df.columns:
        transformed_df["city"] = (
            transformed_df["city"]
            .str.strip()
            .str.title()
        )

    # Convert customer ID to integer
    if "customer_id" in transformed_df.columns:
        transformed_df["customer_id"] = (
            pd.to_numeric(
                transformed_df["customer_id"],
                errors="raise"
            ).astype("int64")
        )

    # Convert age to integer
    if "age" in transformed_df.columns:
        transformed_df["age"] = (
            pd.to_numeric(
                transformed_df["age"],
                errors="raise"
            ).astype("int64")
        )

    # Standardize optional phone numbers
    if "phone_number" in transformed_df.columns:
        transformed_df["phone_number"] = (
            transformed_df["phone_number"]
            .astype("string")
            .str.strip()
        )

    print("\nCustomer data transformation completed!")

    return transformed_df


import pandas as pd
import re


def validate_customer_data(df, contract, run_id, source_file, processed_at):
    """
    Validate customer records using JSON contract rules.

    Uses pandas vectorized operations for better performance.
    Adds pipeline metadata and separates valid and rejected records.
    """

    columns = contract["columns"]

    # Maintain one list of errors for each input record.
    errors_by_row = [[] for _ in range(len(df))]

    for column, rules in columns.items():

        # Handle missing columns.
        if column not in df.columns:
            if rules.get("required", False):
                for errors in errors_by_row:
                    errors.append(f"{column} column is missing")
            continue

        values = df[column]

        # Identify missing and empty values.
        missing = (
            values.isna()
            | values.astype("string").str.strip().eq("").fillna(False)
        )

        if rules.get("required", False):
            for position in missing[missing].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    f"{column} is required"
                )

        # Optional empty values do not need further validation.
        present = ~missing

        expected_type = rules.get("type")

        # Integer validation.
        if expected_type == "integer":
            numeric_values = pd.to_numeric(values, errors="coerce")

            invalid = (
                present
                & (
                    numeric_values.isna()
                    | (numeric_values % 1 != 0)
                )
            )

            for position in invalid[invalid].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    f"{column} must be a valid integer"
                )

        # Number validation.
        elif expected_type == "number":
            numeric_values = pd.to_numeric(values, errors="coerce")

            invalid = present & numeric_values.isna()

            for position in invalid[invalid].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    f"{column} must be a valid number"
                )

        # String validation.
        elif expected_type == "string":
            is_string = values.map(lambda value: isinstance(value, str))
            invalid = present & ~is_string

            for position in invalid[invalid].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    f"{column} must be a string"
                )

        # Email format validation.
        if rules.get("format") == "email":
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

            valid_email = (
                values.astype("string")
                .str.match(email_pattern, na=False)
            )

            invalid = present & ~valid_email

            for position in invalid[invalid].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    "Invalid email format"
                )

        # Minimum value validation.
        if "min" in rules:
            numeric_values = pd.to_numeric(values, errors="coerce")
            invalid = present & numeric_values.notna() & (
                numeric_values < rules["min"]
            )

            for position in invalid[invalid].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    f"{column} must be at least {rules['min']}"
                )

        # Maximum value validation.
        if "max" in rules:
            numeric_values = pd.to_numeric(values, errors="coerce")
            invalid = present & numeric_values.notna() & (
                numeric_values > rules["max"]
            )

            for position in invalid[invalid].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    f"{column} must be at most {rules['max']}"
                )

        # Uniqueness validation.
        if rules.get("unique", False):
            normalized_values = values.astype("string").str.strip()

            duplicates = (
                normalized_values.duplicated(keep="first")
                & present
            )

            for position in duplicates[duplicates].index:
                row_position = df.index.get_loc(position)
                errors_by_row[row_position].append(
                    f"Duplicate value in {column}"
                )

    # Add pipeline metadata without modifying the original DataFrame.
    result_df = df.copy()

    result_df["run_id"] = run_id
    result_df["source_file"] = source_file
    result_df["processed_at"] = processed_at

    # Separate valid and rejected records.
    has_errors = pd.Series(
        [bool(errors) for errors in errors_by_row],
        index=df.index
    )

    result_df["rejection_reason"] = [
        "; ".join(errors) if errors else ""
        for errors in errors_by_row
    ]

    valid_df = result_df.loc[~has_errors].drop(
        columns=["rejection_reason"]
    ).copy()

    rejected_df = result_df.loc[has_errors].copy()

    return valid_df, rejected_df

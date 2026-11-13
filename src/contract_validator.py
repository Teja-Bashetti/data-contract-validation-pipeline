
import json
import pandas as pd


def load_contract(contract_path):
    """
    Load the data contract from a JSON file.
    """

    with open(contract_path, "r") as file:
        contract = json.load(file)

    print("Customer data contract loaded successfully!")

    return contract


def matches_type(value, expected_type):
    """
    Check whether a value matches the expected data type.
    """

    if pd.isna(value):
        return True

    if expected_type == "integer":

        if isinstance(value, bool):
            return False

        try:
            number = float(value)
            return number.is_integer()
        except (ValueError, TypeError):
            return False

    elif expected_type == "number":

        if isinstance(value, bool):
            return False

        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    elif expected_type == "string":
        return isinstance(value, str)

    elif expected_type == "boolean":
        return isinstance(value, bool)

    return False


def validate_schema(df, contract):
    """
    Validate required columns, unexpected columns,
    and column data types.
    """

    expected_columns = list(contract["columns"].keys())
    actual_columns = list(df.columns)

    # Check missing required columns
    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
        and contract["columns"][column].get("required", False)
    ]

    # Check unexpected columns
    unexpected_columns = [
        column
        for column in actual_columns
        if column not in expected_columns
    ]

    # Check data types
    type_errors = []

    for column, rules in contract["columns"].items():

        if column not in df.columns:
            continue

        expected_type = rules["type"]

        for index, value in df[column].items():

            if not matches_type(value, expected_type):

                type_errors.append({
                    "row_number": int(index) + 1,
                    "column": column,
                    "value": str(value),
                    "expected_type": expected_type
                })

    # Final schema validation status
    is_valid = (
        len(missing_columns) == 0
        and len(type_errors) == 0
    )

    schema_result = {
        "dataset": contract["dataset"],
        "contract_version": contract["version"],
        "is_valid": is_valid,
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "type_errors": type_errors
    }

    return schema_result


def compare_contracts(old_contract, new_contract):
    """
    Compare old and new contract versions.
    Identify breaking and non-breaking changes.
    """

    old_columns = old_contract["columns"]
    new_columns = new_contract["columns"]

    breaking_changes = []
    non_breaking_changes = []

    # Check changes to existing columns
    for column, old_rules in old_columns.items():

        if column not in new_columns:

            breaking_changes.append(
                f"Column '{column}' was removed"
            )

            continue

        new_rules = new_columns[column]

        if old_rules["type"] != new_rules["type"]:

            breaking_changes.append(
                f"Column '{column}' changed type "
                f"from {old_rules['type']} to {new_rules['type']}"
            )

        if (
            old_rules.get("required", False) is False
            and new_rules.get("required", False) is True
        ):

            breaking_changes.append(
                f"Column '{column}' changed from optional to required"
            )

        if (
            old_rules.get("unique", False) is False
            and new_rules.get("unique", False) is True
        ):

            breaking_changes.append(
                f"Column '{column}' now requires unique values"
            )

    # Check newly added columns
    for column, new_rules in new_columns.items():

        if column not in old_columns:

            if new_rules.get("required", False):

                breaking_changes.append(
                    f"New column '{column}' is required"
                )

            else:

                non_breaking_changes.append(
                    f"Optional column '{column}' was added"
                )

    evolution_result = {
        "old_version": old_contract["version"],
        "new_version": new_contract["version"],
        "breaking_changes": breaking_changes,
        "non_breaking_changes": non_breaking_changes,
        "is_compatible": len(breaking_changes) == 0
    }

    return evolution_result


import pandas as pd
import pytest

from src.contract_validator import compare_contracts
from src.data_quality import validate_customer_data
from src.transform import transform_customer_data


# Reusable customer contract
def get_customer_contract():
    return {
        "dataset": "customers",
        "version": "1.1",
        "columns": {
            "customer_id": {
                "type": "integer",
                "required": True,
                "unique": True
            },
            "customer_name": {
                "type": "string",
                "required": True
            },
            "email": {
                "type": "string",
                "required": True,
                "format": "email"
            },
            "age": {
                "type": "integer",
                "required": True,
                "min": 18,
                "max": 100
            },
            "city": {
                "type": "string",
                "required": True
            }
        }
    }


def make_contract(version, columns):
    return {
        "dataset": "customers",
        "version": version,
        "columns": columns
    }


# TEST 1: Adding an optional column is non-breaking
def test_optional_column_addition_is_non_breaking():
    old_contract = get_customer_contract()
    new_contract = get_customer_contract()

    new_contract["version"] = "1.2"
    new_contract["columns"]["phone_number"] = {
        "type": "string",
        "required": False
    }

    result = compare_contracts(old_contract, new_contract)

    assert result["is_compatible"] is True
    assert len(result["breaking_changes"]) == 0
    assert len(result["non_breaking_changes"]) == 1


# TEST 2: Changing a column type is breaking
def test_type_change_is_breaking():
    old_contract = get_customer_contract()
    new_contract = get_customer_contract()

    new_contract["version"] = "1.2"
    new_contract["columns"]["age"]["type"] = "string"

    result = compare_contracts(old_contract, new_contract)

    assert result["is_compatible"] is False
    assert any("changed type" in change for change in result["breaking_changes"])


# TEST 3: Invalid age should be rejected
def test_invalid_age_is_rejected():
    df = pd.DataFrame({
        "customer_id": [101],
        "customer_name": ["Ravi"],
        "email": ["ravi@gmail.com"],
        "age": ["thirty"],
        "city": ["Hyderabad"]
    })

    valid_df, rejected_df = validate_customer_data(
        df, get_customer_contract(),
        "test-run", "test.csv", "2026-11-13"
    )

    assert len(valid_df) == 0
    assert len(rejected_df) == 1


# TEST 4: Duplicate customer IDs should be rejected
def test_duplicate_customer_id_is_rejected():
    df = pd.DataFrame({
        "customer_id": [101, 101],
        "customer_name": ["Ravi", "Teja"],
        "email": ["ravi@gmail.com", "teja@gmail.com"],
        "age": [25, 26],
        "city": ["Hyderabad", "Bangalore"]
    })

    valid_df, rejected_df = validate_customer_data(
        df, get_customer_contract(),
        "test-run", "test.csv", "2026-11-13"
    )

    assert len(valid_df) == 1
    assert len(rejected_df) == 1
    assert "Duplicate value in customer_id" in rejected_df.iloc[0]["rejection_reason"]


# TEST 5: Missing customer name should be rejected
def test_missing_customer_name_is_rejected():
    df = pd.DataFrame({
        "customer_id": [102],
        "customer_name": [None],
        "email": ["test@gmail.com"],
        "age": [25],
        "city": ["Hyderabad"]
    })

    valid_df, rejected_df = validate_customer_data(
        df, get_customer_contract(),
        "test-run", "test.csv", "2026-11-13"
    )

    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "customer_name is required" in rejected_df.iloc[0]["rejection_reason"]


# TEST 6: Transformation should clean customer data
def test_customer_data_transformation():
    df = pd.DataFrame({
        "customer_id": ["101"],
        "customer_name": ["  ravi kumar  "],
        "email": [" RAVI@GMAIL.COM "],
        "age": ["25"],
        "city": [" hyderabad "]
    })

    transformed_df = transform_customer_data(df)

    assert transformed_df.iloc[0]["customer_id"] == 101
    assert transformed_df.iloc[0]["customer_name"] == "Ravi Kumar"
    assert transformed_df.iloc[0]["email"] == "ravi@gmail.com"
    assert transformed_df.iloc[0]["age"] == 25
    assert transformed_df.iloc[0]["city"] == "Hyderabad"


# TEST 7: Transformation should not modify original DataFrame
def test_transformation_does_not_modify_original():
    df = pd.DataFrame({
        "customer_id": ["101"],
        "customer_name": ["  ravi kumar  "],
        "email": [" RAVI@GMAIL.COM "],
        "age": ["25"],
        "city": [" hyderabad "]
    })

    original_df = df.copy(deep=True)

    transform_customer_data(df)

    pd.testing.assert_frame_equal(df, original_df)


# TEST 8: Invalid email should be rejected
def test_invalid_email_is_rejected():
    df = pd.DataFrame({
        "customer_id": [201],
        "customer_name": ["Ravi"],
        "email": ["invalid-email"],
        "age": [25],
        "city": ["Hyderabad"]
    })

    valid_df, rejected_df = validate_customer_data(
        df, get_customer_contract(),
        "test-run", "test.csv", "2026-11-13"
    )

    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "Invalid email format" in rejected_df.iloc[0]["rejection_reason"]


# TEST 9: Age below minimum and above maximum should be rejected
@pytest.mark.parametrize("age", [17, 101])
def test_age_out_of_range_is_rejected(age):
    df = pd.DataFrame({
        "customer_id": [202],
        "customer_name": ["Teja"],
        "email": ["teja@gmail.com"],
        "age": [age],
        "city": ["Bangalore"]
    })

    valid_df, rejected_df = validate_customer_data(
        df, get_customer_contract(),
        "test-run", "test.csv", "2026-11-13"
    )

    assert len(valid_df) == 0
    assert len(rejected_df) == 1


# TEST 10: Empty optional field should be accepted
def test_empty_optional_phone_number_is_accepted():
    df = pd.DataFrame({
        "customer_id": [203],
        "customer_name": ["Arun"],
        "email": ["arun@gmail.com"],
        "age": [30],
        "city": ["Chennai"],
        "phone_number": [None]
    })

    contract = get_customer_contract()
    contract["columns"]["phone_number"] = {
        "type": "string",
        "required": False
    }

    valid_df, rejected_df = validate_customer_data(
        df, contract,
        "test-run", "test.csv", "2026-11-13"
    )

    assert len(valid_df) == 1
    assert len(rejected_df) == 0


# TEST 11: Multiple errors should be captured for one record
def test_multiple_validation_errors_are_captured():
    df = pd.DataFrame({
        "customer_id": [204],
        "customer_name": ["Priya"],
        "email": ["wrong-email"],
        "age": [15],
        "city": ["Mumbai"]
    })

    valid_df, rejected_df = validate_customer_data(
        df, get_customer_contract(),
        "test-run", "test.csv", "2026-11-13"
    )

    assert len(valid_df) == 0
    assert len(rejected_df) == 1

    reason = rejected_df.iloc[0]["rejection_reason"]

    assert "Invalid email format" in reason
    assert "age must be at least 18" in reason


# TEST 12: Pipeline metadata should be added to records
def test_pipeline_metadata_is_added():
    df = pd.DataFrame({
        "customer_id": [205],
        "customer_name": ["Kiran"],
        "email": ["kiran@gmail.com"],
        "age": [28],
        "city": ["Delhi"]
    })

    valid_df, rejected_df = validate_customer_data(
        df,
        get_customer_contract(),
        "my-test-run",
        "customers.csv",
        "2026-11-13T10:00:00"
    )

    assert len(valid_df) == 1
    assert len(rejected_df) == 0

    assert valid_df.iloc[0]["run_id"] == "my-test-run"
    assert valid_df.iloc[0]["source_file"] == "customers.csv"
    assert valid_df.iloc[0]["processed_at"] == "2026-11-13T10:00:00"

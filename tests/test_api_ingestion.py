
from unittest.mock import Mock, patch

import pytest
import requests

from src.api_ingestion import read_users_from_api


# Helper: Create a successful fake API response
def create_mock_response():

    response = Mock()

    response.json.return_value = [
        {
            "id": 1,
            "name": "Ravi",
            "email": "ravi@gmail.com",
            "address": {
                "city": "Hyderabad"
            }
        },
        {
            "id": 2,
            "name": "Teja",
            "email": "teja@gmail.com",
            "address": {
                "city": "Bangalore"
            }
        }
    ]

    return response


# TEST 1: Successful API response
@patch("src.api_ingestion.requests.get")
def test_api_success(mock_get):

    mock_get.return_value = create_mock_response()

    df = read_users_from_api()

    assert len(df) == 2
    assert "customer_id" in df.columns
    assert "customer_name" in df.columns
    assert "email" in df.columns
    assert "city" in df.columns

    assert df.iloc[0]["customer_name"] == "Ravi"
    assert df.iloc[0]["city"] == "Hyderabad"


# TEST 2: API timeout followed by successful retry
@patch("src.api_ingestion.time.sleep")
@patch("src.api_ingestion.requests.get")
def test_api_timeout_then_retry(mock_get, mock_sleep):

    mock_get.side_effect = [
        requests.exceptions.Timeout(),
        create_mock_response()
    ]

    df = read_users_from_api()

    assert len(df) == 2
    assert mock_get.call_count == 2
    assert mock_sleep.call_count == 1


# TEST 3: API fails after all retry attempts
@patch("src.api_ingestion.time.sleep")
@patch("src.api_ingestion.requests.get")
def test_api_failure_after_three_attempts(mock_get, mock_sleep):

    mock_get.side_effect = requests.exceptions.Timeout()

    with pytest.raises(RuntimeError):

        read_users_from_api()

    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2

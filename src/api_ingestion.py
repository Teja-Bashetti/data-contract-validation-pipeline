
import requests
import pandas as pd
import time


def read_users_from_api():

    """
    Fetch customer records from a REST API.
    Handle network errors, HTTP errors and timeouts.
    Retry failed requests up to 3 times.
    """

    api_url = "https://jsonplaceholder.typicode.com/users"

    max_retries = 3
    timeout_seconds = 10

    print("Connecting to API...")

    for attempt in range(1, max_retries + 1):

        try:

            print(f"API request attempt: {attempt}")

            response = requests.get(
                api_url,
                timeout=timeout_seconds
            )

            # Raise an exception for unsuccessful HTTP status codes
            response.raise_for_status()

            # Convert API response into JSON
            users = response.json()

            if not isinstance(users, list):
                raise ValueError("API response must contain a list of users.")

            print("API data received successfully!")

            # Convert JSON into Pandas DataFrame
            df = pd.json_normalize(users)

            # Rename API columns
            df = df.rename(columns={
                "id": "customer_id",
                "name": "customer_name",
                "address.city": "city"
            })

            # Check required API fields
            required_columns = [
                "customer_id",
                "customer_name",
                "email",
                "city"
            ]

            missing_columns = [
                column for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"API response is missing columns: {missing_columns}"
                )

            # Select required columns
            df = df[required_columns]

            print("\nAPI data converted into DataFrame!")
            print(df.head())

            print("\nTotal API records:", len(df))

            return df

        except requests.exceptions.HTTPError as error:

            status_code = (
                error.response.status_code
                if error.response is not None
                else None
            )

            print("HTTP error:", error)

            # Retry only for temporary server errors or rate limiting
            if status_code not in [429, 500, 502, 503, 504]:
                raise

        except requests.exceptions.Timeout:

            print("API request timed out!")

        except requests.exceptions.ConnectionError:

            print("Unable to connect to API. Check your internet connection.")

        except requests.exceptions.RequestException as error:

            print("Request error:", error)

        except ValueError as error:

            # Invalid JSON or unexpected API response structure
            raise RuntimeError(
                f"Invalid API response: {error}"
            ) from error

        # Wait before retrying, but not after the final attempt
        if attempt < max_retries:

            wait_seconds = attempt * 2

            print(
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        f"API ingestion failed after {max_retries} attempts."
    )


if __name__ == "__main__":

    customers_df = read_users_from_api()

    customers_df.to_csv(
        "data/input/api_customers.csv",
        index=False
    )

    print("\nAPI data saved to CSV successfully!")

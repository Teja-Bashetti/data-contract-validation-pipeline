
import json
import re
from pathlib import Path

import pandas as pd
import requests


CSV_PATH = Path("data/input/customers.csv")
OUTPUT_PATH = Path("config/customer_contract_ai_proposal.json")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


def validate_proposed_contract(contract, csv_columns):
    """
    Check that the AI-generated contract follows
    the structure expected by our existing pipeline.
    """

    if not isinstance(contract, dict):
        raise ValueError("Contract must be a JSON object.")

    required_keys = {"dataset", "version", "description", "columns"}

    if not required_keys.issubset(contract.keys()):
        raise ValueError("AI contract is missing required top-level fields.")

    if not isinstance(contract["columns"], dict):
        raise ValueError("Contract columns must be a JSON object.")

    allowed_types = {"integer", "string", "float", "boolean"}

    for column, rules in contract["columns"].items():

        if not isinstance(rules, dict):
            raise ValueError(f"Invalid rules for column: {column}")

        if rules.get("type") not in allowed_types:
            raise ValueError(f"Unsupported data type for {column}")

        if not isinstance(rules.get("required"), bool):
            raise ValueError(f"Invalid required rule for {column}")

    missing_columns = set(csv_columns) - set(contract["columns"])

    if missing_columns:
        raise ValueError(
            f"AI contract missed CSV columns: {missing_columns}"
        )

    return True


def generate_contract():

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    # Read sample CSV records
    df = pd.read_csv(CSV_PATH)

    sample_data = df.head(5).to_dict(orient="records")

    columns = list(df.columns)

    prompt = f"""
You are a data engineering assistant.

Generate a proposed JSON data contract for this CSV dataset.

CSV columns:
{json.dumps(columns)}

Sample records:
{json.dumps(sample_data, default=str)}

Return ONLY valid JSON. Do not use Markdown code fences.

Use exactly this structure:

{{
  "dataset": "customers",
  "version": "1.0",
  "description": "Proposed customer data contract",
  "columns": {{
    "customer_id": {{
      "type": "integer",
      "required": true,
      "unique": true
    }}
  }}
}}

Rules:
1. Include every CSV column.
2. Allowed types are integer, string, float, boolean.
3. Use required as true or false.
4. Use unique only when appropriate.
5. Use format=email for email fields when appropriate.
6. Use min and max only when justified by sample data and common business rules.
7. Do not invent columns.
8. This is a proposal. Do not claim that inferred rules are confirmed business rules.
"""

    print("Sending CSV sample to local AI model...")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "format": "json",
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()

    result = response.json()

    ai_output = result.get("response", "").strip()

    # Remove Markdown code fences if the model adds them
    ai_output = re.sub(r"^```(?:json)?\s*", "", ai_output)
    ai_output = re.sub(r"\s*```$", "", ai_output)

    # Convert AI response into a Python dictionary
    contract = json.loads(ai_output)

    # Validate the proposed contract structure
    validate_proposed_contract(contract, columns)

    # Create output folder if necessary
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save proposal separately from the production contract
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(contract, file, indent=4)

    print("\nAI contract proposal generated successfully!")
    print("Saved to:", OUTPUT_PATH)

    print("\nProposed contract:")
    print(json.dumps(contract, indent=4))


if __name__ == "__main__":

    try:
        generate_contract()

    except requests.exceptions.ConnectionError:
        print("ERROR: Ollama is not running. Start Ollama and try again.")

    except requests.exceptions.Timeout:
        print("ERROR: AI request timed out. Try again.")

    except requests.exceptions.RequestException as error:
        print("ERROR: Ollama API request failed:", error)

    except (ValueError, json.JSONDecodeError) as error:
        print("ERROR: AI generated an invalid contract:", error)

    except Exception as error:
        print("ERROR:", error)

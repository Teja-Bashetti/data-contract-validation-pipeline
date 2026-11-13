
import os
import uuid
import time
from datetime import datetime, timezone

from src.logger import get_logger
from src.api_ingestion import read_users_from_api
from src.contract_validator import (
    load_contract,
    validate_schema
)
from src.data_quality import validate_customer_data
from src.transform import transform_customer_data


# Create API pipeline logger
logger = get_logger("api_pipeline")


def main():

    # STEP 1: Start pipeline
    start_time = time.perf_counter()

    run_id = str(uuid.uuid4())
    processed_at = datetime.now(timezone.utc).isoformat()

    logger.info("========== API PIPELINE STARTED ==========")
    logger.info("Run ID: %s", run_id)
    logger.info("Started at: %s", processed_at)

    try:

        # STEP 2: Read data from API
        customers_df = read_users_from_api()

        logger.info(
            "API data loaded successfully. Total records: %s",
            len(customers_df)
        )

        # STEP 3: Load API contract
        contract = load_contract(
            "config/customer_api_contract.json"
        )

        logger.info(
            "API contract loaded. Version: %s",
            contract["version"]
        )

        # STEP 4: Validate API schema
        schema_result = validate_schema(
            customers_df,
            contract
        )

        logger.info("========== API SCHEMA VALIDATION ==========")
        logger.info("Schema validation result: %s", schema_result)

        if schema_result["missing_columns"]:
            raise ValueError(
                "Required API columns are missing: "
                f"{schema_result['missing_columns']}"
            )

        if schema_result["type_errors"]:
            logger.warning("API data type errors detected.")
            logger.warning(
                "Invalid records will be checked individually."
            )

        # STEP 5: Validate individual records
        valid_df, rejected_df = validate_customer_data(
            customers_df,
            contract,
            run_id,
            "REST API",
            processed_at
        )

        logger.info("========== DATA QUALITY RESULTS ==========")
        logger.info("Valid records: %s", len(valid_df))
        logger.info("Rejected records: %s", len(rejected_df))

        # STEP 6: Transform valid records
        valid_df = transform_customer_data(valid_df)

        logger.info("API customer data transformation completed.")

        # STEP 7: Save API pipeline outputs
        os.makedirs("data/valid", exist_ok=True)
        os.makedirs("data/rejected", exist_ok=True)

        valid_df.to_csv(
            "data/valid/api_customers_valid.csv",
            index=False
        )

        rejected_df.to_csv(
            "data/rejected/api_customers_rejected.csv",
            index=False
        )

        logger.info(
            "Valid records saved: data/valid/api_customers_valid.csv"
        )

        logger.info(
            "Rejected records saved: data/rejected/api_customers_rejected.csv"
        )

        # STEP 8: Calculate execution time
        execution_time = round(
            time.perf_counter() - start_time,
            3
        )

        # STEP 9: Display final results
        logger.info("========== API PIPELINE RESULTS ==========")

        logger.info("Run ID: %s", run_id)
        logger.info("Total records: %s", len(customers_df))
        logger.info("Valid records: %s", len(valid_df))
        logger.info("Rejected records: %s", len(rejected_df))
        logger.info("Execution time: %s seconds", execution_time)

        logger.info("========== API PIPELINE COMPLETED ==========")

    except Exception:
        logger.exception("API pipeline execution failed.")
        raise


if __name__ == "__main__":
    main()


import uuid
import time
import os
from datetime import datetime, timezone

import pandas as pd

from src.logger import get_logger
from src.ingestion import read_customer_csv
from src.data_quality import validate_customer_data
from src.transform import transform_customer_data
from src.database import publish_customers

from src.contract_validator import (
    load_contract,
    validate_schema,
    compare_contracts
)


# Create logger
logger = get_logger()


def main():

    # STEP 1: Start pipeline execution
    start_time = time.perf_counter()

    run_id = str(uuid.uuid4())
    processed_at = datetime.now(timezone.utc).isoformat()

    logger.info("========== PIPELINE STARTED ==========")
    logger.info("Run ID: %s", run_id)
    logger.info("Started at: %s", processed_at)

    try:

        # STEP 2: Read customer CSV
        file_path = "data/input/customers.csv"

        customers_df = read_customer_csv(file_path)

        logger.info(
            "CSV loaded successfully. Total records: %s",
            len(customers_df)
        )

        # STEP 3: Load latest data contract
        contract_path = "config/customer_contract.json"

        contract = load_contract(contract_path)

        logger.info(
            "Customer contract loaded. Version: %s",
            contract["version"]
        )

        # STEP 4: Validate incoming CSV schema
        schema_result = validate_schema(customers_df, contract)

        logger.info("========== SCHEMA VALIDATION ==========")
        logger.info("Schema validation result: %s", schema_result)

        if schema_result["missing_columns"]:
            raise ValueError(
                "Required columns are missing: "
                f"{schema_result['missing_columns']}"
            )

        if schema_result["type_errors"]:

            logger.warning("Data type errors detected!")

            for error in schema_result["type_errors"]:
                logger.warning(
                    "Row %s: %s = %s (expected %s)",
                    error["row_number"],
                    error["column"],
                    error["value"],
                    error["expected_type"]
                )

            logger.warning(
                "Invalid records will be handled by data quality validation."
            )

        # STEP 5: Compare contract versions
        old_contract_path = "config/customer_contract_v1.json"

        old_contract = load_contract(old_contract_path)

        evolution_result = compare_contracts(
            old_contract,
            contract
        )

        logger.info("========== CONTRACT EVOLUTION ==========")
        logger.info("Evolution result: %s", evolution_result)

        for change in evolution_result["breaking_changes"]:
            logger.error("Breaking change: %s", change)

        for change in evolution_result["non_breaking_changes"]:
            logger.info("Non-breaking change: %s", change)

        if not evolution_result["is_compatible"]:
            raise ValueError(
                "Contract compatibility check failed. "
                "Breaking schema changes detected."
            )

        logger.info("Contract compatibility check passed.")

        # STEP 6: Validate individual customer records
        valid_df, rejected_df = validate_customer_data(
            customers_df,
            contract,
            run_id,
            file_path,
            processed_at
        )

        logger.info("========== DATA QUALITY RESULTS ==========")
        logger.info("Valid records: %s", len(valid_df))
        logger.info("Rejected records: %s", len(rejected_df))

        # STEP 7: Transform valid records
        valid_df = transform_customer_data(valid_df)

        logger.info("Customer data transformation completed.")

        # STEP 8: Save transformed valid records
        os.makedirs("data/valid", exist_ok=True)

        valid_df.to_csv(
            "data/valid/customers_valid.csv",
            index=False
        )

        logger.info("Transformed valid records saved successfully.")

        # STEP 9: Save rejected records
        os.makedirs("data/rejected", exist_ok=True)

        rejected_df.to_csv(
            "data/rejected/customers_rejected.csv",
            index=False
        )

        logger.info("Rejected records saved successfully.")

        # STEP 10: Publish transformed records to SQLite
        publish_customers(valid_df)

        logger.info("SQLite publishing completed successfully.")

        # STEP 11: Calculate pipeline metrics
        total_records = len(customers_df)
        valid_records = len(valid_df)
        rejected_records = len(rejected_df)

        success_rate = (
            round(valid_records / total_records * 100, 2)
            if total_records > 0 else 0
        )

        rejection_rate = (
            round(rejected_records / total_records * 100, 2)
            if total_records > 0 else 0
        )

        execution_time = round(
            time.perf_counter() - start_time,
            3
        )

        # STEP 12: Create metrics report
        metrics = {
            "run_id": run_id,
            "processed_at": processed_at,
            "source_file": file_path,
            "dataset": contract["dataset"],
            "contract_version": contract["version"],
            "total_records": total_records,
            "valid_records": valid_records,
            "rejected_records": rejected_records,
            "success_rate": success_rate,
            "rejection_rate": rejection_rate,
            "execution_time_seconds": execution_time,
            "status": (
                "SUCCESS_WITH_REJECTIONS"
                if rejected_records > 0
                else "SUCCESS"
            )
        }

        # STEP 13: Save metrics history
        os.makedirs("reports", exist_ok=True)

        metrics_path = "reports/run_metrics.csv"

        metrics_df = pd.DataFrame([metrics])

        metrics_df.to_csv(
            metrics_path,
            mode="a",
            header=not os.path.exists(metrics_path),
            index=False
        )

        logger.info("Metrics report saved: %s", metrics_path)

        # STEP 14: Display final results
        logger.info("========== FINAL PIPELINE RESULTS ==========")

        logger.info("Run ID: %s", run_id)
        logger.info("Total records: %s", total_records)
        logger.info("Valid records: %s", valid_records)
        logger.info("Rejected records: %s", rejected_records)

        logger.info("Success rate: %s%%", success_rate)
        logger.info("Rejection rate: %s%%", rejection_rate)

        logger.info("Execution time: %s seconds", execution_time)

        logger.info("========== PIPELINE COMPLETED ==========")

    except Exception:
        logger.exception("Pipeline execution failed.")
        raise


if __name__ == "__main__":
    main()

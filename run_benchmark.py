
import os
import time
import uuid
from datetime import datetime, timezone

import pandas as pd

from src.logger import get_logger
from src.contract_validator import load_contract, validate_schema
from src.data_quality import validate_customer_data
from src.transform import transform_customer_data


# Create benchmark logger
logger = get_logger("benchmark_pipeline")


def run_benchmark():

    start_time = time.perf_counter()

    run_id = str(uuid.uuid4())
    processed_at = datetime.now(timezone.utc).isoformat()

    timings = {}

    input_path = "data/input/customers_100k.csv"

    logger.info("========== 100K CUSTOMER PIPELINE BENCHMARK STARTED ==========")
    logger.info("Run ID: %s", run_id)
    logger.info("Started at: %s", processed_at)

    try:

        # STEP 1: Read the 100,000-row CSV file
        stage_start = time.perf_counter()

        customers_df = pd.read_csv(input_path)

        timings["csv_read_seconds"] = (
            time.perf_counter() - stage_start
        )

        logger.info("1. CSV ingestion completed.")
        logger.info("Records loaded: %s", len(customers_df))

        # Estimate memory used by the input DataFrame
        memory_mb = (
            customers_df.memory_usage(deep=True).sum()
            / (1024 * 1024)
        )

        logger.info("Input DataFrame memory: %.2f MB", memory_mb)

        # STEP 2: Load the data contract
        stage_start = time.perf_counter()

        contract = load_contract(
            "config/customer_contract.json"
        )

        timings["contract_load_seconds"] = (
            time.perf_counter() - stage_start
        )

        logger.info(
            "2. Data contract loaded. Version: %s",
            contract["version"]
        )

        # STEP 3: Validate the input schema
        stage_start = time.perf_counter()

        schema_result = validate_schema(
            customers_df,
            contract
        )

        timings["schema_validation_seconds"] = (
            time.perf_counter() - stage_start
        )

        logger.info("3. Schema validation result: %s", schema_result)

        if (
            schema_result.get("missing_columns")
            or schema_result.get("type_errors")
        ):

            logger.error(
                "Benchmark stopped: schema validation failed."
            )

            if schema_result.get("missing_columns"):
                logger.error(
                    "Missing columns: %s",
                    schema_result["missing_columns"]
                )

            if schema_result.get("type_errors"):
                logger.error(
                    "Schema type errors: %s",
                    schema_result["type_errors"]
                )

            return

        logger.info("Schema validation passed.")

        # STEP 4: Validate individual records
        stage_start = time.perf_counter()

        valid_df, rejected_df = validate_customer_data(
            customers_df,
            contract,
            run_id,
            input_path,
            processed_at
        )

        timings["data_quality_seconds"] = (
            time.perf_counter() - stage_start
        )

        logger.info("4. Data quality validation completed.")
        logger.info("Valid records: %s", len(valid_df))
        logger.info("Rejected records: %s", len(rejected_df))

        # STEP 5: Transform valid records
        stage_start = time.perf_counter()

        transformed_df = transform_customer_data(valid_df)

        timings["transformation_seconds"] = (
            time.perf_counter() - stage_start
        )

        logger.info("5. Data transformation completed.")
        logger.info("Transformed records: %s", len(transformed_df))

        # STEP 6: Save benchmark output files
        stage_start = time.perf_counter()

        os.makedirs("data/valid", exist_ok=True)
        os.makedirs("data/rejected", exist_ok=True)
        os.makedirs("reports", exist_ok=True)

        transformed_df.to_csv(
            "data/valid/customers_100k_valid.csv",
            index=False
        )

        rejected_df.to_csv(
            "data/rejected/customers_100k_rejected.csv",
            index=False
        )

        timings["output_write_seconds"] = (
            time.perf_counter() - stage_start
        )

        logger.info("6. Benchmark output files saved.")
        logger.info(
            "Valid output: data/valid/customers_100k_valid.csv"
        )
        logger.info(
            "Rejected output: data/rejected/customers_100k_rejected.csv"
        )

        # STEP 7: Calculate total processing time
        total_seconds = sum(timings.values())

        success_rate = (
            len(transformed_df) / len(customers_df) * 100
            if len(customers_df) > 0 else 0
        )

        logger.info("========== BENCHMARK RESULTS ==========")

        for stage, seconds in timings.items():
            logger.info("%s: %.4f seconds", stage, seconds)

        logger.info("---------------------------------------")
        logger.info(
            "Total processing time: %.4f seconds",
            total_seconds
        )
        logger.info("Total input records: %s", len(customers_df))
        logger.info("Valid records: %s", len(transformed_df))
        logger.info("Rejected records: %s", len(rejected_df))
        logger.info("Input memory usage: %.2f MB", memory_mb)
        logger.info("Success rate: %.2f%%", success_rate)

        # STEP 8: Save benchmark metrics
        benchmark_result = {
            "run_id": run_id,
            "processed_at": processed_at,
            "input_file": input_path,
            "total_records": len(customers_df),
            "valid_records": len(transformed_df),
            "rejected_records": len(rejected_df),
            "success_rate": round(success_rate, 2),
            "input_memory_mb": round(memory_mb, 2),
            **timings,
            "total_processing_seconds": round(total_seconds, 4)
        }

        report_path = "reports/benchmark_metrics.csv"

        report_df = pd.DataFrame([benchmark_result])

        if os.path.exists(report_path):
            report_df.to_csv(
                report_path,
                mode="a",
                header=False,
                index=False
            )
        else:
            report_df.to_csv(
                report_path,
                index=False
            )

        logger.info(
            "Benchmark metrics saved to: %s",
            report_path
        )

        logger.info(
            "Total execution time including reporting: %.4f seconds",
            time.perf_counter() - start_time
        )

        logger.info("========== BENCHMARK COMPLETED ==========")

    except Exception:
        logger.exception("Benchmark pipeline execution failed.")
        raise


if __name__ == "__main__":
    run_benchmark()

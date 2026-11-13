
# Data Contract & Schema Evolution Validation Pipeline

## 1. Project Overview

This project implements a data engineering pipeline that validates customer data using JSON-based data contracts.

It supports CSV files, REST APIs, and large datasets. It detects schema changes, validates data quality, transforms customer records, and separates valid and rejected records.

The project also includes automated testing, logging, and performance benchmarking.

## 2. Business Problem

In real-world data engineering, data received from different sources may contain:

- Missing columns
- Incorrect data types
- Duplicate customer records
- Invalid email addresses
- Missing required values
- Unexpected schema changes

These problems can cause data pipeline failures and unreliable reporting.

This project addresses these issues through contract-based schema validation and data quality checks.

## 3. Architecture

```text
                DATA SOURCES
                     |
          +----------+----------+
          |          |          |
         CSV       REST API    100K CSV
          |          |          |
          +----------+----------+
                     |
              DATA INGESTION
                     |
             JSON DATA CONTRACT
                     |
             SCHEMA VALIDATION
                     |
           CONTRACT EVOLUTION
                     |
             DATA QUALITY CHECKS
                     |
              DATA TRANSFORMATION
                     |
          +----------+----------+
          |          |          |
        VALID      REJECTED    SQLITE
        DATA        DATA       DATABASE
          |          |
          +----------+
                     |
             METRICS & LOGGING
                     |
              PYTEST TESTING
```

## 4. Technologies Used

- Python
- Pandas
- SQL
- SQLite
- REST APIs
- JSON
- Pytest
- Logging
- Git and GitHub
- VS Code

## 5. Project Structure

```text
data_contract_validation_pipeline/
|
|-- config/
|   |-- customer_contract.json
|   |-- customer_contract_v1.json
|   |-- customer_contract_breaking.json
|   |-- customer_api_contract.json
|
|-- data/
|   |-- input/
|   |-- valid/
|   |-- rejected/
|   |-- customer_data.db
|
|-- logs/
|   |-- pipeline.log
|
|-- reports/
|   |-- run_metrics.csv
|   |-- benchmark_metrics.csv
|
|-- src/
|   |-- ingestion.py
|   |-- contract_validator.py
|   |-- data_quality.py
|   |-- database.py
|   |-- transform.py
|   |-- api_ingestion.py
|   |-- generate_test_data.py
|   |-- logger.py
|
|-- tests/
|   |-- test_pipeline.py
|   |-- test_api_ingestion.py
|
|-- run_ingestion.py
|-- run_api_pipeline.py
|-- run_benchmark.py
|-- README.md
|-- requirements.txt
```

## 6. Key Features

### Data Ingestion
- Reads customer data from CSV files.
- Fetches customer data from REST APIs.
- Supports large datasets.

### Data Contract Validation
- Uses JSON contracts to define expected schemas.
- Checks required and optional columns.
- Validates data types.
- Detects breaking and non-breaking schema changes.

### Data Quality Validation
- Checks required fields.
- Validates email formats.
- Detects duplicate customer IDs.
- Checks minimum and maximum values.
- Separates valid and rejected records.

### Data Transformation
- Standardizes customer names and city names.
- Converts email addresses to lowercase.
- Converts numeric columns to appropriate types.

### Database Publishing
- Publishes validated customer records into SQLite.
- Uses customer_id for record updates.

### Monitoring and Logging
- Maintains pipeline execution logs.
- Records run IDs and execution timestamps.
- Tracks valid and rejected records.
- Stores pipeline metrics.

### Performance Benchmarking
- Generates and processes 100,000 customer records.
- Measures execution time for individual pipeline stages.
- Tracks memory usage and success rate.

## 7. Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd data_contract_validation_pipeline
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 8. Execute the Pipelines

### CSV Pipeline

```bash
python run_ingestion.py
```

### REST API Pipeline

```bash
python run_api_pipeline.py
```

### Generate 100K Test Records

```bash
python -m src.generate_test_data
```

### Run Performance Benchmark

```bash
python run_benchmark.py
```

## 9. Run Automated Tests

```bash
pytest -v
```

The current project has 16 passing automated test cases.

## 10. Benchmark Results

Latest recorded benchmark:

| Metric | Result |
|---|---:|
| Total records | 100,000 |
| Valid records | 100,000 |
| Rejected records | 0 |
| Input memory | 19.55 MB |
| Processing time | 2.174 seconds |
| Success rate | 100% |

Benchmark results may vary depending on the execution environment.

## 11. Output Files

Valid records:

- data/valid/customers_valid.csv
- data/valid/api_customers_valid.csv
- data/valid/customers_100k_valid.csv

Rejected records:

- data/rejected/customers_rejected.csv
- data/rejected/api_customers_rejected.csv
- data/rejected/customers_100k_rejected.csv

Reports:

- reports/run_metrics.csv
- reports/benchmark_metrics.csv

Logs:

- logs/pipeline.log

Database:

- data/customer_data.db

## 12. Learning Outcomes

This project demonstrates practical knowledge of:

- Python-based data engineering
- Data ingestion from multiple sources
- Data contracts and schema evolution
- Data quality validation
- REST API integration
- Data transformation
- SQL and SQLite
- Automated testing
- Logging and monitoring
- Performance optimization

## 13. Future Enhancements

- AWS S3 integration
- AWS Glue data processing
- Amazon Redshift integration
- Apache Airflow orchestration
- Docker containerization
- Data quality monitoring dashboard

---

**Author:** Your Name

**Project:** Data Contract & Schema Evolution Validation Pipeline

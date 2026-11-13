# Troubleshooting Guide

This guide explains common problems when running the Data Contract & Schema Evolution Validation Pipeline.

## 1. ModuleNotFoundError: No module named 'src'

**Cause:** Python cannot recognize the `src` directory as a package.

**Solution:**

Make sure this file exists:

```text
src/__init__.py
```

Run tests using:

```powershell
python -m pytest -v
```

## 2. CSV file not found

**Cause:** The input CSV file is missing or the path is incorrect.

**Solution:**

Check that this file exists:

```text
data/input/customers.csv
```

## 3. Ollama connection error

**Cause:** The local Ollama service is not running.

**Solution:**

Start Ollama if it is not already running. Then execute:

```powershell
python ai_contract_generator.py
```

If port 11434 is already in use, Ollama may already be running. Do not start another server unnecessarily.

## 4. AI model not found

**Cause:** The requested Ollama model is not installed.

**Solution:**

Run:

```powershell
ollama list
```

If `qwen2.5:1.5b` is missing, install it:

```powershell
ollama pull qwen2.5:1.5b
```

## 5. Invalid data type

**Cause:** A CSV value does not match the expected data type in the contract.

**Example:**

```text
age = thirty
```

Expected type:

```text
integer
```

**Solution:** Correct the source data or send the invalid record to the rejected records output for review.

## 6. SQLite database locked

**Cause:** Another process may be accessing the SQLite database.

**Solution:**

Close database viewers or other scripts using the database and retry the pipeline.

## 7. Tests failing

**Solution:**

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install project dependencies:

```powershell
pip install -r requirements.txt
```

Run the test suite:

```powershell
python -m pytest -v
```

## 8. AI-generated contract contains incorrect rules

**Cause:** An AI model can suggest rules that do not represent actual business requirements.

**Solution:**

Review the generated file:

```text
config/customer_contract_ai_proposal.json
```

Compare it with the approved production contract:

```text
config/customer_contract.json
```

Never automatically replace the production contract with an AI-generated proposal. Get approval from the data owner first.

---

**Important:** The pipeline uses deterministic validation rules for actual data processing. AI is used only to assist with contract generation.

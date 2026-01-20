# Integration Tests

## Overview

Integration tests verify the action works against a **real Snowflake instance**. These tests are **skipped by default** and only run when explicitly requested.

## Setup

### 1. Set Environment Variables

```bash
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_DATABASE="your-database"
export SNOWFLAKE_SCHEMA="your-schema"
```

### 2. Ensure You Have Write Permissions

The integration tests will:
- Create test tables with unique names (e.g., `test_glossary_a1b2c3d4`)
- Insert test data
- Clean up (drop tables) after each test

## Running Integration Tests

### Run Only Integration Tests

```bash
pytest -m integration tests/test_snowflake_integration.py -v
```

### Run All Tests (Including Integration)

```bash
pytest -m "" tests/ -v
```

### Run Unit Tests Only (Default)

```bash
pytest tests/
# or
pytest -m "not integration" tests/
```

## What's Tested

### Table Creation
- ✅ Glossary table schema is correct
- ✅ Usage table schema is correct
- ✅ All expected columns exist
- ✅ Tables can be created and dropped

### Data Insertion
- ✅ Glossary rows insert correctly
- ✅ Usage rows insert correctly
- ✅ Data is retrievable and accurate
- ✅ TRUNCATE works (new inserts replace old data)

### Data Types
- ✅ VARCHAR columns handle URNs and names
- ✅ VARIANT columns handle JSON (custom_properties, ownership)
- ✅ TIMESTAMP columns work correctly
- ✅ Composite primary keys work

## Test Coverage

| Test | What It Verifies |
|------|------------------|
| `test_create_and_drop_glossary_table` | Table creation with correct schema |
| `test_create_and_drop_usage_table` | Usage table creation with correct schema |
| `test_insert_glossary_rows` | Inserting and retrieving glossary data |
| `test_insert_usage_rows` | Inserting and retrieving usage data |
| `test_insert_with_truncate` | TRUNCATE behavior on re-insert |

## Safety Features

1. **Unique table names** - Each test uses UUID-based table names to avoid conflicts
2. **Automatic cleanup** - Tables are dropped after each test
3. **Isolated tests** - Each test creates its own tables
4. **Skip on failure** - If Snowflake connection fails, tests are skipped (not failed)

## CI/CD Integration

To run integration tests in CI/CD, set the environment variables as secrets and run:

```bash
pytest -m integration tests/test_snowflake_integration.py --tb=short
```

## Troubleshooting

### "Snowflake connection not available"
- Check your environment variables are set correctly
- Verify your Snowflake credentials are valid
- Ensure you have network access to Snowflake

### Permission Errors
- Verify your user has `CREATE TABLE` and `DROP TABLE` permissions
- Ensure you can write to the specified database/schema

### Table Already Exists
- This shouldn't happen (tests use unique names)
- If it does, manually drop the table and re-run

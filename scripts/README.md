# Utility Scripts

This directory contains utility scripts for testing and verification.

## Scripts

### test_graphql_live.py
Tests GraphQL queries against a live DataHub instance.

**Usage:**
```bash
# Edit the script to set GMS_SERVER and TOKEN
python scripts/test_graphql_live.py
```

**What it does:**
- Fetches all glossary terms from DataHub
- Tests the usage query for each term
- Shows which dashboards use each glossary term
- Verifies the GraphQL query works correctly

### test_snowflake_writes.py
Comprehensive end-to-end test of Snowflake writes with Pydantic models.

**Usage:**
```bash
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_DATABASE="your-database"
export SNOWFLAKE_SCHEMA="your-schema"

python scripts/test_snowflake_writes.py
```

**What it tests:**
- ✅ Pydantic model creation and validation
- ✅ Table creation with correct schemas
- ✅ Data insertion with model_dump()
- ✅ JSON/VARIANT column parsing
- ✅ Special character handling
- ✅ Timestamp conversion
- ✅ NULL value handling
- ✅ Data retrieval and verification

### test_graphql_query.graphql
Example GraphQL query for testing glossary term usage.

**Usage:**
1. Copy the query content
2. Open DataHub's GraphiQL interface (http://your-datahub:8080/api/graphiql)
3. Paste the query
4. Set variables with a real glossary term URN
5. Execute to see which entities use that term

**Default behavior:** Searches for DASHBOARD entities only (matches the action default)

## When to Use These Scripts

- **Before first deployment** - Run `test_snowflake_writes.py` to verify Snowflake setup
- **Testing new GraphQL queries** - Use `test_graphql_live.py` and `test_graphql_query.graphql`
- **Troubleshooting** - Run these scripts to isolate issues
- **Verifying data** - Check that glossary terms and usage are being captured correctly

## See Also

- [Integration Tests Guide](../docs/INTEGRATION_TESTS.md) - How to run integration tests
- [Integration Test Code](../tests/test_snowflake_integration.py) - Automated pytest integration tests
- [Test Verification Guide](../docs/TEST_VERIFICATION.md) - Complete verification checklist
- [Unit Tests](../tests/test_glossary_export_action.py) - Automated unit tests

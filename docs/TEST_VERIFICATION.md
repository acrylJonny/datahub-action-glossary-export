# Test Verification Checklist

This document outlines how to verify the refactored code works correctly, especially with Snowflake writes.

## ✅ Unit Tests (Automated)

Run all unit tests with mocked dependencies:

```bash
# Run all unit tests
pytest tests/test_glossary_export_action.py -v

# Expected: 20 tests pass
```

**What's tested:**
- ✅ Configuration validation
- ✅ Pydantic model creation and validation
- ✅ Data transformation (GraphQL → Pydantic models)
- ✅ SQL generation
- ✅ model_dump() conversion
- ✅ Special characters handling

## ✅ Type Checking (Automated)

Verify type safety:

```bash
mypy action_glossary_export/ tests/
```

**Expected:** No errors

## ✅ Integration Tests (Manual - Requires Snowflake)

### Option 1: Run Integration Test Suite

```bash
# Set environment variables
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_DATABASE="your-database"
export SNOWFLAKE_SCHEMA="your-schema"

# Run integration tests
pytest -m integration tests/test_snowflake_integration.py -v
```

**What's tested:**
- ✅ Table creation with correct schema
- ✅ Pydantic models → Snowflake INSERT
- ✅ Data retrieval and validation
- ✅ TRUNCATE behavior
- ✅ Composite primary keys

### Option 2: Run Comprehensive Manual Test

```bash
# Set environment variables (same as above)

# Run detailed test script
python scripts/test_snowflake_writes.py
```

**What's tested:**
- ✅ End-to-end flow with realistic data
- ✅ VARIANT columns (JSON parsing)
- ✅ TIMESTAMP conversion
- ✅ Special characters: apostrophes, quotes, symbols, Unicode
- ✅ NULL handling
- ✅ model_validate() → model_dump() → SQL INSERT flow

**Test data includes:**
- Complex custom properties (nested JSON)
- Ownership lists
- Special characters: `apostrophe's`, `"quotes"`, `100%`, `360°`, `<>&`
- NULL values for optional fields
- Timestamps

## 🔍 What to Look For

### 1. JSON/VARIANT Parsing

Check that VARIANT columns handle complex data:

```sql
SELECT custom_properties, ownership FROM test_glossary_*;
```

**Expected:**
- Valid JSON in VARIANT columns
- No parsing errors
- Nested structures preserved

### 2. Special Characters

Verify special characters are preserved:

```sql
SELECT description, entity_name FROM test_* WHERE description LIKE '%apostrophe%';
```

**Expected:**
- Apostrophes: `'`
- Quotes: `"`
- Symbols: `%`, `&`, `<`, `>`, `°`
- All preserved correctly

### 3. Timestamps

Check timestamp conversion:

```sql
SELECT created_at, last_updated FROM test_glossary_* WHERE created_at IS NOT NULL;
```

**Expected:**
- Millisecond timestamps → TIMESTAMP_NTZ
- Correct date/time values

### 4. Primary Keys

Verify composite keys work:

```sql
-- Try to insert duplicate (should fail)
INSERT INTO test_usage_* (glossary_term_urn, entity_urn, ...) 
VALUES ('same-urn', 'same-urn', ...);
```

**Expected:** Primary key violation error

## 🐛 Common Issues to Watch For

### Issue 1: JSON Serialization Errors

**Symptom:**
```
Error: Unable to PARSE_JSON
```

**Root cause:** Incorrect use of `model_dump()` or missing JSON serialization

**Verification:** Check `snowflake.py` lines 87-90 and 158

### Issue 2: Type Mismatches

**Symptom:**
```
TypeError: Object of type X is not JSON serializable
```

**Root cause:** Pydantic model not converted to dict before JSON encoding

**Verification:** Ensure all `row.model_dump()` calls before `json.dumps()`

### Issue 3: SQL Injection Vulnerability

**Symptom:** Special characters break SQL

**Root cause:** Not using parameterized queries

**Verification:** All VALUES use `%(field)s` placeholders, never f-strings

### Issue 4: NULL Handling

**Symptom:**
```
Error: Cannot insert NULL into required field
```

**Root cause:** Pydantic model validation vs SQL constraints mismatch

**Verification:** Check `models.py` Optional fields match Snowflake schema

## ✅ Verification Steps Completed

After running tests, check off:

- [ ] All 20 unit tests pass
- [ ] MyPy type checking passes with 0 errors
- [ ] Integration tests pass (or manual test script)
- [ ] Special characters preserved in Snowflake
- [ ] JSON/VARIANT columns parse correctly
- [ ] Timestamps convert properly
- [ ] Composite primary keys work
- [ ] No SQL injection vulnerabilities

## 📝 Test Results Template

Document your test results:

```
Date: _________
Tester: _________
Snowflake Account: _________

Unit Tests: PASS / FAIL
Type Checking: PASS / FAIL
Integration Tests: PASS / FAIL / SKIPPED

Notes:
- 
- 
- 

Issues Found:
- 
- 
```

## 🚀 Production Readiness

Before deploying to production:

1. ✅ All automated tests pass
2. ✅ Manual Snowflake write test successful
3. ✅ Special characters tested with production-like data
4. ✅ Performance acceptable (check insert times in logs)
5. ✅ No linter warnings (`ruff check action_glossary_export/`)
6. ✅ Documentation updated
7. ✅ CHANGELOG.md updated

## 📞 Troubleshooting

If tests fail:

1. Check environment variables are set correctly
2. Verify Snowflake credentials have CREATE TABLE permissions
3. Check network access to Snowflake
4. Review error logs for specific issues
5. Run with verbose logging: `pytest -v -s`

For persistent issues, check:
- `action_glossary_export/models.py` - Field definitions
- `action_glossary_export/transformers.py` - model_validate() calls
- `action_glossary_export/snowflake.py` - model_dump() and SQL generation

"""
Integration tests for Snowflake operations.

These tests require a real Snowflake connection and are skipped by default.
Run with: pytest -m integration tests/test_snowflake_integration.py

Set environment variables:
- SNOWFLAKE_ACCOUNT
- SNOWFLAKE_USER
- SNOWFLAKE_PASSWORD
- SNOWFLAKE_DATABASE
- SNOWFLAKE_SCHEMA
"""

import os

import pytest
from pydantic import SecretStr

from action_glossary_export.models import GlossaryRow, UsageRow
from action_glossary_export.snowflake import (
    create_glossary_table,
    create_usage_table,
    insert_glossary_rows,
    insert_usage_rows,
)

try:
    from datahub.ingestion.source.snowflake.snowflake_connection import (
        SnowflakeConnectionConfig,
    )
except ImportError:
    SnowflakeConnectionConfig = None  # type: ignore

pytestmark = pytest.mark.integration


@pytest.fixture
def snowflake_connection():
    """Create a real Snowflake connection for integration tests."""
    if SnowflakeConnectionConfig is None:
        pytest.skip("DataHub Snowflake connector not available")

    try:
        account = os.environ.get("SNOWFLAKE_ACCOUNT")
        username = os.environ.get("SNOWFLAKE_USER")
        password = os.environ.get("SNOWFLAKE_PASSWORD")

        if not account or not username or not password:
            pytest.skip("Snowflake credentials not set in environment variables")

        config = SnowflakeConnectionConfig(
            account_id=account,
            username=username,
            password=SecretStr(password),
        )
        conn = config.get_native_connection()

        # Set database and schema
        cursor = conn.cursor()
        try:
            cursor.execute(f"USE DATABASE {os.environ.get('SNOWFLAKE_DATABASE')}")
            cursor.execute(f"USE SCHEMA {os.environ.get('SNOWFLAKE_SCHEMA')}")
        finally:
            cursor.close()

        yield conn

        # Cleanup
        conn.close()

    except Exception as e:
        pytest.skip(f"Snowflake connection not available: {e}")


@pytest.fixture
def test_table_name():
    """Generate a unique test table name."""
    import uuid

    return f"test_glossary_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_usage_table_name():
    """Generate a unique test usage table name."""
    import uuid

    return f"test_usage_{uuid.uuid4().hex[:8]}"


class TestSnowflakeIntegration:
    """Integration tests for Snowflake operations."""

    def test_create_and_drop_glossary_table(self, snowflake_connection, test_table_name):
        """Test creating and dropping glossary table in Snowflake."""
        # Create table
        create_glossary_table(snowflake_connection, test_table_name)

        # Verify table exists
        cursor = snowflake_connection.cursor()
        try:
            cursor.execute(f"DESCRIBE TABLE {test_table_name}")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            # Check for expected columns
            assert "URN" in column_names
            assert "NAME" in column_names
            assert "ENTITY_TYPE" in column_names
            assert "DESCRIPTION" in column_names
            assert "CUSTOM_PROPERTIES" in column_names

        finally:
            # Cleanup
            cursor.execute(f"DROP TABLE IF EXISTS {test_table_name}")
            cursor.close()

    def test_create_and_drop_usage_table(
        self, snowflake_connection, test_usage_table_name
    ):
        """Test creating and dropping usage table in Snowflake."""
        # Create table
        create_usage_table(snowflake_connection, test_usage_table_name)

        # Verify table exists
        cursor = snowflake_connection.cursor()
        try:
            cursor.execute(f"DESCRIBE TABLE {test_usage_table_name}")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            # Check for expected columns
            assert "GLOSSARY_TERM_URN" in column_names
            assert "GLOSSARY_TERM_NAME" in column_names
            assert "ENTITY_URN" in column_names
            assert "ENTITY_NAME" in column_names
            assert "PLATFORM" in column_names

        finally:
            # Cleanup
            cursor.execute(f"DROP TABLE IF EXISTS {test_usage_table_name}")
            cursor.close()

    def test_insert_glossary_rows(self, snowflake_connection, test_table_name):
        """Test inserting glossary rows into Snowflake."""
        # Create table
        create_glossary_table(snowflake_connection, test_table_name)

        cursor = snowflake_connection.cursor()
        try:
            # Sample data
            rows = [
                GlossaryRow(
                    urn="urn:li:glossaryTerm:test-term-1",
                    name="Test Term 1",
                    entity_type="glossary_term",
                    description="Test description",
                    hierarchical_path="Test Term 1",
                    custom_properties={"key1": "value1"},
                ),
                GlossaryRow(
                    urn="urn:li:glossaryTerm:test-term-2",
                    name="Test Term 2",
                    entity_type="glossary_term",
                    description="Another test",
                    hierarchical_path="Test Term 2",
                ),
            ]

            # Insert rows
            insert_glossary_rows(snowflake_connection, test_table_name, rows)

            # Verify rows were inserted
            cursor.execute(f"SELECT COUNT(*) FROM {test_table_name}")
            count = cursor.fetchone()[0]
            assert count == 2

            # Verify data
            cursor.execute(f"SELECT urn, name FROM {test_table_name} ORDER BY urn")
            results = cursor.fetchall()
            assert results[0][0] == "urn:li:glossaryTerm:test-term-1"
            assert results[0][1] == "Test Term 1"
            assert results[1][0] == "urn:li:glossaryTerm:test-term-2"
            assert results[1][1] == "Test Term 2"

        finally:
            # Cleanup
            cursor.execute(f"DROP TABLE IF EXISTS {test_table_name}")
            cursor.close()

    def test_insert_usage_rows(self, snowflake_connection, test_usage_table_name):
        """Test inserting usage rows into Snowflake."""
        # Create table
        create_usage_table(snowflake_connection, test_usage_table_name)

        cursor = snowflake_connection.cursor()
        try:
            # Sample data
            rows = [
                UsageRow(
                    glossary_term_urn="urn:li:glossaryTerm:revenue",
                    glossary_term_name="Revenue",
                    entity_urn="urn:li:dashboard:(powerbi,sales)",
                    entity_name="Sales Dashboard",
                    entity_type="dashboard",
                    entity_subtype="Report",
                    platform="powerbi",
                    container_urn="urn:li:container:workspace",
                    container_name="Workspace",
                    domain_urn="urn:li:domain:finance",
                    domain_name="Finance",
                )
            ]

            # Insert rows
            insert_usage_rows(snowflake_connection, test_usage_table_name, rows)

            # Verify rows were inserted
            cursor.execute(f"SELECT COUNT(*) FROM {test_usage_table_name}")
            count = cursor.fetchone()[0]
            assert count == 1

            # Verify data
            cursor.execute(
                f"SELECT glossary_term_urn, entity_urn, platform FROM {test_usage_table_name}"
            )
            result = cursor.fetchone()
            assert result[0] == "urn:li:glossaryTerm:revenue"
            assert result[1] == "urn:li:dashboard:(powerbi,sales)"
            assert result[2] == "powerbi"

        finally:
            # Cleanup
            cursor.execute(f"DROP TABLE IF EXISTS {test_usage_table_name}")
            cursor.close()

    def test_insert_with_truncate(self, snowflake_connection, test_table_name):
        """Test that insert truncates existing data."""
        # Create table
        create_glossary_table(snowflake_connection, test_table_name)

        cursor = snowflake_connection.cursor()
        try:
            # First insert
            rows_1 = [
                GlossaryRow(
                    urn="urn:li:glossaryTerm:term-1",
                    name="Term 1",
                    entity_type="glossary_term",
                    hierarchical_path="Term 1",
                )
            ]
            insert_glossary_rows(snowflake_connection, test_table_name, rows_1)

            cursor.execute(f"SELECT COUNT(*) FROM {test_table_name}")
            assert cursor.fetchone()[0] == 1

            # Second insert (should truncate first)
            rows_2 = [
                GlossaryRow(
                    urn="urn:li:glossaryTerm:term-2",
                    name="Term 2",
                    entity_type="glossary_term",
                    hierarchical_path="Term 2",
                ),
                GlossaryRow(
                    urn="urn:li:glossaryTerm:term-3",
                    name="Term 3",
                    entity_type="glossary_term",
                    hierarchical_path="Term 3",
                ),
            ]
            insert_glossary_rows(snowflake_connection, test_table_name, rows_2)

            # Should only have 2 rows (truncated first insert)
            cursor.execute(f"SELECT COUNT(*) FROM {test_table_name}")
            assert cursor.fetchone()[0] == 2

        finally:
            # Cleanup
            cursor.execute(f"DROP TABLE IF EXISTS {test_table_name}")
            cursor.close()

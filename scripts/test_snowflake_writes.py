#!/usr/bin/env python3
"""
Manual test script to verify Snowflake writes work correctly with Pydantic models.

This script tests the complete flow:
1. Create Pydantic models with realistic data
2. Transform to dict using model_dump()
3. Insert into Snowflake
4. Verify data retrieval

Run with Snowflake credentials:
    export SNOWFLAKE_ACCOUNT="your-account"
    export SNOWFLAKE_USER="your-username"
    export SNOWFLAKE_PASSWORD="your-password"
    export SNOWFLAKE_DATABASE="your-database"
    export SNOWFLAKE_SCHEMA="your-schema"

    python test_snowflake_writes.py
"""

import json
import os
import sys
from datetime import datetime

from pydantic import SecretStr

# Import our models and functions
from action_glossary_export.models import GlossaryRow, UsageRow
from action_glossary_export.snowflake import (
    create_glossary_table,
    create_usage_table,
    insert_glossary_rows,
    insert_usage_rows,
)


def get_snowflake_connection():
    """Get a Snowflake connection using environment variables."""
    try:
        from datahub.ingestion.source.snowflake.snowflake_connection import (
            SnowflakeConnectionConfig,
        )
    except ImportError:
        print("ERROR: datahub package not installed. Install with: pip install acryl-datahub")
        sys.exit(1)

    account = os.environ.get("SNOWFLAKE_ACCOUNT")
    username = os.environ.get("SNOWFLAKE_USER")
    password = os.environ.get("SNOWFLAKE_PASSWORD")
    database = os.environ.get("SNOWFLAKE_DATABASE")
    schema = os.environ.get("SNOWFLAKE_SCHEMA")

    if not all([account, username, password, database, schema]):
        print("ERROR: Missing required environment variables:")
        print("  SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD,")
        print("  SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA")
        sys.exit(1)

    # Type assertions - we've checked these are not None above
    assert account is not None
    assert username is not None
    assert password is not None
    assert database is not None
    assert schema is not None

    print(f"Connecting to Snowflake: {account} / {database}.{schema}")

    config = SnowflakeConnectionConfig(
        account_id=account,
        username=username,
        password=SecretStr(password),
    )
    conn = config.get_native_connection()

    # Set database and schema
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE DATABASE {database}")
        cursor.execute(f"USE SCHEMA {schema}")
        print("✅ Connected successfully")
    finally:
        cursor.close()

    return conn


def create_test_glossary_data():
    """Create realistic test data for glossary rows."""
    rows = [
        GlossaryRow(
            urn="urn:li:glossaryTerm:revenue",
            name="Revenue",
            entity_type="glossary_term",
            description="Total revenue from all sources including sales, subscriptions, and services",
            parent_node_urn="urn:li:glossaryNode:finance",
            parent_node_name="Finance",
            hierarchical_path="Finance > Revenue",
            domain_urn="urn:li:domain:finance-domain",
            domain_name="Finance Domain",
            custom_properties={"classification": "Financial", "sensitivity": "High"},
            ownership=[
                {"urn": "urn:li:corpuser:jsmith", "username": "jsmith", "type": "TECHNICAL_OWNER"}
            ],
            created_at=1642521600000,  # 2022-01-18
        ),
        GlossaryRow(
            urn="urn:li:glossaryNode:finance",
            name="Finance",
            entity_type="glossary_node",
            description="Finance related terms and metrics",
            hierarchical_path="Finance",
            domain_urn="urn:li:domain:finance-domain",
            domain_name="Finance Domain",
        ),
        GlossaryRow(
            urn="urn:li:glossaryTerm:customer-id",
            name="Customer ID",
            entity_type="glossary_term",
            description='Unique identifier for customers with special chars: apostrophe\'s, "quotes", and 100% symbols!',
            hierarchical_path="Customer ID",
        ),
    ]
    return rows


def create_test_usage_data():
    """Create realistic test data for usage rows."""
    rows = [
        UsageRow(
            glossary_term_urn="urn:li:glossaryTerm:revenue",
            glossary_term_name="Revenue",
            entity_urn="urn:li:dashboard:(powerbi,sales-dashboard)",
            entity_name="Sales Performance Dashboard",
            entity_type="dashboard",
            entity_subtype="Report",
            platform="powerbi",
            container_urn="urn:li:container:sales-workspace",
            container_name="Sales Workspace",
            domain_urn="urn:li:domain:sales",
            domain_name="Sales",
        ),
        UsageRow(
            glossary_term_urn="urn:li:glossaryTerm:revenue",
            glossary_term_name="Revenue",
            entity_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.revenue_table,PROD)",
            entity_name="revenue_table",
            entity_type="dataset",
            entity_subtype="Table",
            platform="snowflake",
            container_urn="urn:li:container:db.schema",
            container_name="schema",
            domain_urn="urn:li:domain:analytics",
            domain_name="Analytics",
        ),
        UsageRow(
            glossary_term_urn="urn:li:glossaryTerm:customer-id",
            glossary_term_name="Customer ID",
            entity_urn="urn:li:dashboard:(tableau,customer-360)",
            entity_name="Customer 360° View with special chars: <>&\"'",
            entity_type="dashboard",
            platform="tableau",
        ),
    ]
    return rows


def verify_glossary_data(conn, table_name, expected_count):
    """Verify glossary data was inserted correctly."""
    cursor = conn.cursor()
    try:
        print(f"\n📊 Verifying glossary data in {table_name}...")

        # Check count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Row count: {count} (expected: {expected_count})")
        assert count == expected_count, f"Expected {expected_count} rows, got {count}"

        # Check data types and sample data
        cursor.execute(
            f"""
            SELECT urn, name, entity_type, description, custom_properties, ownership, created_at
            FROM {table_name}
            ORDER BY urn
            """
        )
        rows = cursor.fetchall()

        for row in rows:
            urn, name, entity_type, description, custom_props, ownership, created_at = row
            print(f"\n  ✓ {urn}")
            print(f"    Name: {name}")
            print(f"    Type: {entity_type}")
            if custom_props:
                print(f"    Custom Props (VARIANT): {json.loads(custom_props)}")
            if ownership:
                print(f"    Ownership (VARIANT): {json.loads(ownership)}")
            if created_at:
                print(f"    Created: {created_at}")

        # Test special characters handling
        cursor.execute(
            f"""
            SELECT description
            FROM {table_name}
            WHERE urn = 'urn:li:glossaryTerm:customer-id'
            """
        )
        result = cursor.fetchone()
        if result:
            desc = result[0]
            assert "apostrophe's" in desc, "Apostrophe not preserved"
            assert '"quotes"' in desc, "Quotes not preserved"
            assert "100%" in desc, "Percent sign not preserved"
            print(f"\n  ✓ Special characters handled correctly: {desc[:50]}...")

    finally:
        cursor.close()


def verify_usage_data(conn, table_name, expected_count):
    """Verify usage data was inserted correctly."""
    cursor = conn.cursor()
    try:
        print(f"\n📊 Verifying usage data in {table_name}...")

        # Check count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Row count: {count} (expected: {expected_count})")
        assert count == expected_count, f"Expected {expected_count} rows, got {count}"

        # Check composite primary key works
        cursor.execute(
            f"""
            SELECT glossary_term_urn, entity_urn, entity_name, platform
            FROM {table_name}
            ORDER BY glossary_term_urn, entity_urn
            """
        )
        rows = cursor.fetchall()

        for row in rows:
            term_urn, entity_urn, entity_name, platform = row
            print(f"\n  ✓ {term_urn} -> {entity_urn}")
            print(f"    Entity: {entity_name}")
            print(f"    Platform: {platform or 'None'}")

        # Test special characters in entity names
        cursor.execute(
            f"""
            SELECT entity_name
            FROM {table_name}
            WHERE entity_urn = 'urn:li:dashboard:(tableau,customer-360)'
            """
        )
        result = cursor.fetchone()
        if result:
            name = result[0]
            assert "360°" in name, "Degree symbol not preserved"
            assert "<>&" in name, "Special chars not preserved"
            print(f"\n  ✓ Special characters in entity name: {name}")

    finally:
        cursor.close()


def main():
    """Run the complete test."""
    print("=" * 70)
    print("SNOWFLAKE WRITE TEST - Pydantic Models")
    print("=" * 70)

    # Get connection
    conn = get_snowflake_connection()

    # Generate unique table names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    glossary_table = f"test_glossary_{timestamp}"
    usage_table = f"test_usage_{timestamp}"

    try:
        # Test 1: Create tables
        print("\n1️⃣ Creating test tables...")
        create_glossary_table(conn, glossary_table)
        print(f"  ✅ Created {glossary_table}")
        create_usage_table(conn, usage_table)
        print(f"  ✅ Created {usage_table}")

        # Test 2: Insert glossary data
        print("\n2️⃣ Inserting glossary data...")
        glossary_rows = create_test_glossary_data()
        print(f"  Created {len(glossary_rows)} Pydantic GlossaryRow objects")
        insert_glossary_rows(conn, glossary_table, glossary_rows)
        print("  ✅ Inserted successfully")

        # Test 3: Insert usage data
        print("\n3️⃣ Inserting usage data...")
        usage_rows = create_test_usage_data()
        print(f"  Created {len(usage_rows)} Pydantic UsageRow objects")
        insert_usage_rows(conn, usage_table, usage_rows)
        print("  ✅ Inserted successfully")

        # Test 4: Verify glossary data
        verify_glossary_data(conn, glossary_table, len(glossary_rows))
        print("  ✅ Glossary data verified")

        # Test 5: Verify usage data
        verify_usage_data(conn, usage_table, len(usage_rows))
        print("  ✅ Usage data verified")

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nTest tables created:")
        print(f"  - {glossary_table}")
        print(f"  - {usage_table}")
        print("\nTo inspect manually:")
        print(f"  SELECT * FROM {glossary_table};")
        print(f"  SELECT * FROM {usage_table};")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        # Cleanup
        cleanup = input("\nClean up test tables? (y/n): ").lower().strip()
        if cleanup == "y":
            cursor = conn.cursor()
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {glossary_table}")
                cursor.execute(f"DROP TABLE IF EXISTS {usage_table}")
                print("✅ Cleaned up test tables")
            finally:
                cursor.close()

        conn.close()
        print("\n👋 Done!")


if __name__ == "__main__":
    main()

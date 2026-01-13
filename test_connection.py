#!/usr/bin/env python3
"""
Quick test script to verify Snowflake and DataHub connections before running the action.

Usage:
    export SNOWFLAKE_PASSWORD="your-password"
    export DATAHUB_TOKEN="your-token"
    python test_connection.py
"""

import os
import sys


def test_snowflake_connection():
    """Test Snowflake connection using DataHub's config"""
    print("\n" + "=" * 60)
    print("Testing Snowflake Connection")
    print("=" * 60)

    try:
        from datahub.ingestion.source.snowflake.snowflake_connection import (
            SnowflakeConnectionConfig,
        )
    except ImportError:
        print("❌ Error: DataHub not installed. Run: pip install acryl-datahub")
        return False

    # Get credentials from environment
    account_id = os.getenv("SNOWFLAKE_ACCOUNT_ID", "")
    username = os.getenv("SNOWFLAKE_USERNAME", "")
    password = os.getenv("SNOWFLAKE_PASSWORD", "")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "")
    role = os.getenv("SNOWFLAKE_ROLE", "")

    if not all([account_id, username, password]):
        print("❌ Missing required environment variables:")
        print("   Set: SNOWFLAKE_ACCOUNT_ID, SNOWFLAKE_USERNAME, SNOWFLAKE_PASSWORD")
        print("\nExample:")
        print("   export SNOWFLAKE_ACCOUNT_ID='xy12345'")
        print("   export SNOWFLAKE_USERNAME='datahub_user'")
        print("   export SNOWFLAKE_PASSWORD='your-password'")
        print("   export SNOWFLAKE_WAREHOUSE='COMPUTE_WH'  # Optional")
        print("   export SNOWFLAKE_ROLE='DATAHUB_ROLE'     # Optional")
        return False

    print("\n📋 Configuration:")
    print(f"   Account: {account_id}")
    print(f"   Username: {username}")
    print(f"   Warehouse: {warehouse or '(default)'}")
    print(f"   Role: {role or '(default)'}")

    try:
        # Create connection config
        config = SnowflakeConnectionConfig(
            account_id=account_id,
            username=username,
            password=password,
            warehouse=warehouse if warehouse else None,
            role=role if role else None,
        )

        print("\n🔌 Connecting to Snowflake...")
        conn = config.get_native_connection()

        print("✅ Connection successful!")

        # Test basic query
        cursor = conn.cursor()
        cursor.execute(
            "SELECT CURRENT_VERSION(), CURRENT_WAREHOUSE(), CURRENT_ROLE(), CURRENT_DATABASE()"
        )
        result = cursor.fetchone()

        print("\n📊 Connection Details:")
        print(f"   Snowflake Version: {result[0]}")
        print(f"   Current Warehouse: {result[1]}")
        print(f"   Current Role: {result[2]}")
        print(f"   Current Database: {result[3] or '(none)'}")

        cursor.close()
        conn.close()

        print("\n✅ Snowflake connection test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Snowflake connection FAILED: {e}")
        print("\nTroubleshooting:")
        print("  - Verify account_id is correct (without .snowflakecomputing.com)")
        print("  - Check username and password")
        print("  - Verify network connectivity")
        print("  - Check if IP needs to be allowlisted")
        return False


def test_datahub_connection():
    """Test DataHub GraphQL connection"""
    print("\n" + "=" * 60)
    print("Testing DataHub Connection")
    print("=" * 60)

    try:
        from datahub.ingestion.graph.client import DataHubGraph
    except ImportError:
        print("❌ Error: DataHub not installed. Run: pip install acryl-datahub")
        return False

    # Get credentials from environment
    server = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
    token = os.getenv("DATAHUB_TOKEN", "")

    if not token:
        print("❌ Missing DATAHUB_TOKEN environment variable")
        print("\nExample:")
        print("   export DATAHUB_TOKEN='your-datahub-token'")
        print("   export DATAHUB_GMS_URL='http://localhost:8080'  # Optional")
        return False

    print("\n📋 Configuration:")
    print(f"   Server: {server}")
    print(f"   Token: {'*' * 10}...{token[-4:] if len(token) > 4 else '****'}")

    try:
        from datahub.ingestion.graph.config import DatahubClientConfig

        print("\n🔌 Connecting to DataHub...")

        graph = DataHubGraph(
            config=DatahubClientConfig(
                server=server,
                token=token,
            )
        )

        print("✅ Connection successful!")

        # Test GraphQL query
        print("\n🔍 Testing GraphQL query (searching for glossary terms)...")

        from datahub_actions.api.action_graph import AcrylDataHubGraph

        acryl_graph = AcrylDataHubGraph(graph)

        query = """
        query searchGlossaryTerms($input: SearchInput!) {
            search(input: $input) {
                total
            }
        }
        """

        variables = {
            "input": {
                "type": "GLOSSARY_TERM",
                "query": "*",
                "start": 0,
                "count": 1,
            }
        }

        response = acryl_graph.get_by_graphql_query({"query": query, "variables": variables})

        total_terms = response.get("search", {}).get("total", 0)

        print(f"✅ Found {total_terms} glossary terms in DataHub")

        # Test for nodes too
        variables["input"]["type"] = "GLOSSARY_NODE"
        response = acryl_graph.get_by_graphql_query({"query": query, "variables": variables})

        total_nodes = response.get("search", {}).get("total", 0)

        print(f"✅ Found {total_nodes} glossary nodes in DataHub")

        print("\n✅ DataHub connection test PASSED")

        if total_terms == 0 and total_nodes == 0:
            print("\n⚠️  WARNING: No glossary terms or nodes found.")
            print("   The export will create an empty table.")
            print("   Add some glossary terms in DataHub UI first.")

        return True

    except Exception as e:
        print(f"\n❌ DataHub connection FAILED: {e}")
        print("\nTroubleshooting:")
        print("  - Verify DATAHUB_GMS_URL is correct")
        print("  - Check that token is valid and not expired")
        print("  - Verify network connectivity to DataHub")
        print("  - Check DataHub server is running")
        return False


def test_permissions():
    """Test that Snowflake user has required permissions"""
    print("\n" + "=" * 60)
    print("Testing Snowflake Permissions")
    print("=" * 60)

    try:
        from datahub.ingestion.source.snowflake.snowflake_connection import (
            SnowflakeConnectionConfig,
        )
    except ImportError:
        print("⏭️  Skipping (DataHub not installed)")
        return True

    account_id = os.getenv("SNOWFLAKE_ACCOUNT_ID", "")
    username = os.getenv("SNOWFLAKE_USERNAME", "")
    password = os.getenv("SNOWFLAKE_PASSWORD", "")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "")
    role = os.getenv("SNOWFLAKE_ROLE", "")
    database = os.getenv("SNOWFLAKE_DATABASE", "TEST_DB")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "TEST_SCHEMA")

    if not all([account_id, username, password]):
        print("⏭️  Skipping (missing credentials)")
        return True

    try:
        config = SnowflakeConnectionConfig(
            account_id=account_id,
            username=username,
            password=password,
            warehouse=warehouse if warehouse else None,
            role=role if role else None,
        )

        conn = config.get_native_connection()
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{database}'")
        if not cursor.fetchone():
            print(f"⚠️  Database '{database}' does not exist")
            print(f"   Create it: CREATE DATABASE {database};")
        else:
            print(f"✅ Database '{database}' exists")

        # Try to use the database
        try:
            cursor.execute(f"USE DATABASE {database}")
            print(f"✅ Can access database '{database}'")

            # Check schema
            cursor.execute(f"SHOW SCHEMAS LIKE '{schema}'")
            if not cursor.fetchone():
                print(f"⚠️  Schema '{schema}' does not exist")
                print(f"   Create it: CREATE SCHEMA {database}.{schema};")
            else:
                print(f"✅ Schema '{schema}' exists")

            # Try to use schema
            try:
                cursor.execute(f"USE SCHEMA {schema}")
                print(f"✅ Can access schema '{schema}'")

                # Test table creation permission
                test_table = "datahub_test_" + str(os.getpid())
                try:
                    cursor.execute(f"""
                        CREATE TEMPORARY TABLE {test_table} (
                            id INT,
                            name VARCHAR(100)
                        )
                    """)
                    print(f"✅ Can create tables in '{database}.{schema}'")

                    cursor.execute(f"INSERT INTO {test_table} VALUES (1, 'test')")
                    print("✅ Can insert data")

                    cursor.execute(f"DROP TABLE {test_table}")
                    print("✅ All permissions verified")

                except Exception as e:
                    print(f"❌ Cannot create/insert into tables: {e}")
                    print("\nRequired grants:")
                    print(
                        f"  GRANT CREATE TABLE ON SCHEMA {database}.{schema} TO ROLE {role or 'your_role'};"
                    )
                    print(
                        f"  GRANT INSERT ON ALL TABLES IN SCHEMA {database}.{schema} TO ROLE {role or 'your_role'};"
                    )
                    return False

            except Exception as e:
                print(f"❌ Cannot access schema: {e}")
                return False

        except Exception as e:
            print(f"❌ Cannot access database: {e}")
            return False

        cursor.close()
        conn.close()

        print("\n✅ Permissions test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Permissions test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DataHub Glossary Export - Connection Test Suite")
    print("=" * 60)

    print("\n📝 Instructions:")
    print("   Set these environment variables before running:")
    print("   - SNOWFLAKE_ACCOUNT_ID")
    print("   - SNOWFLAKE_USERNAME")
    print("   - SNOWFLAKE_PASSWORD")
    print("   - SNOWFLAKE_WAREHOUSE (optional)")
    print("   - SNOWFLAKE_ROLE (optional)")
    print("   - SNOWFLAKE_DATABASE (optional, default: TEST_DB)")
    print("   - SNOWFLAKE_SCHEMA (optional, default: TEST_SCHEMA)")
    print("   - DATAHUB_TOKEN")
    print("   - DATAHUB_GMS_URL (optional, default: http://localhost:8080)")

    results = []

    # Test Snowflake
    results.append(("Snowflake Connection", test_snowflake_connection()))

    # Test DataHub
    results.append(("DataHub Connection", test_datahub_connection()))

    # Test Permissions
    results.append(("Snowflake Permissions", test_permissions()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All tests PASSED! Ready to run the action.")
        print("\nNext steps:")
        print("  1. Update snfk_tst.yml with your actual values")
        print("  2. Run: datahub actions -c snfk_tst.yml")
        print("  3. Check Snowflake for the exported table")
        return 0
    else:
        print("\n❌ Some tests FAILED. Fix the issues above before running the action.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

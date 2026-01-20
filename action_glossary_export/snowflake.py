"""Snowflake database operations."""

import json
import logging

from .models import GlossaryRow, UsageRow

logger = logging.getLogger(__name__)


def create_glossary_table(conn, table_name: str) -> None:
    """Create the glossary table if it doesn't exist."""
    cursor = conn.cursor()

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        urn VARCHAR(500) PRIMARY KEY,
        name VARCHAR(500),
        entity_type VARCHAR(50),
        description VARCHAR(16777216),
        parent_node_urn VARCHAR(500),
        parent_node_name VARCHAR(500),
        hierarchical_path VARCHAR(16777216),
        domain_urn VARCHAR(500),
        domain_name VARCHAR(500),
        custom_properties VARIANT,
        ownership VARIANT,
        created_at TIMESTAMP_NTZ,
        last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """

    try:
        cursor.execute(create_table_sql)
        logger.info(f"Table {table_name} created or already exists")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise
    finally:
        cursor.close()


def create_usage_table(conn, table_name: str) -> None:
    """Create the glossary term usage table if it doesn't exist."""
    cursor = conn.cursor()

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        glossary_term_urn VARCHAR(500),
        glossary_term_name VARCHAR(500),
        entity_urn VARCHAR(500),
        entity_name VARCHAR(500),
        entity_type VARCHAR(50),
        entity_subtype VARCHAR(100),
        platform VARCHAR(100),
        container_urn VARCHAR(500),
        container_name VARCHAR(500),
        domain_urn VARCHAR(500),
        domain_name VARCHAR(500),
        last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
        PRIMARY KEY (glossary_term_urn, entity_urn)
    )
    """

    try:
        cursor.execute(create_table_sql)
        logger.info(f"Table {table_name} created or already exists")
    except Exception as e:
        logger.error(f"Error creating usage table: {e}")
        raise
    finally:
        cursor.close()


def insert_glossary_rows(conn, table_name: str, rows: list[GlossaryRow]) -> None:
    """Insert glossary rows into Snowflake table."""
    if not rows:
        logger.info("No rows to insert")
        return

    cursor = conn.cursor()

    try:
        logger.info(f"Truncating table {table_name}...")
        cursor.execute(f"TRUNCATE TABLE {table_name}")

        for i, row in enumerate(rows, 1):
            row_dict = row.model_dump()
            custom_props_json = (
                json.dumps(row_dict["custom_properties"]) if row_dict["custom_properties"] else None
            )
            ownership_json = json.dumps(row_dict["ownership"]) if row_dict["ownership"] else None

            insert_sql = f"""
            INSERT INTO {table_name}
            (urn, name, entity_type, description, parent_node_urn, parent_node_name,
             hierarchical_path, domain_urn, domain_name, custom_properties, ownership, created_at)
            SELECT
                %(urn)s,
                %(name)s,
                %(entity_type)s,
                %(description)s,
                %(parent_node_urn)s,
                %(parent_node_name)s,
                %(hierarchical_path)s,
                %(domain_urn)s,
                %(domain_name)s,
                CASE WHEN %(custom_properties)s IS NULL THEN NULL ELSE PARSE_JSON(%(custom_properties)s) END,
                CASE WHEN %(ownership)s IS NULL THEN NULL ELSE PARSE_JSON(%(ownership)s) END,
                CASE WHEN %(created_at)s IS NULL THEN NULL ELSE TO_TIMESTAMP_NTZ(%(created_at)s, 3) END
            """

            params = {
                "urn": row_dict["urn"],
                "name": row_dict["name"],
                "entity_type": row_dict["entity_type"],
                "description": row_dict["description"],
                "parent_node_urn": row_dict["parent_node_urn"],
                "parent_node_name": row_dict["parent_node_name"],
                "hierarchical_path": row_dict["hierarchical_path"],
                "domain_urn": row_dict["domain_urn"],
                "domain_name": row_dict["domain_name"],
                "custom_properties": custom_props_json,
                "ownership": ownership_json,
                "created_at": row_dict["created_at"],
            }

            cursor.execute(insert_sql, params)

            if i % 100 == 0:
                logger.info(f"Inserted {i}/{len(rows)} rows...")

        conn.commit()
        logger.info(f"Successfully inserted {len(rows)} rows into Snowflake")

    except Exception as e:
        logger.error(f"Error inserting rows to Snowflake: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def insert_usage_rows(conn, table_name: str, rows: list[UsageRow]) -> None:
    """Insert usage rows into Snowflake table."""
    if not rows:
        logger.info("No usage rows to insert")
        return

    cursor = conn.cursor()

    try:
        logger.info(f"Truncating table {table_name}...")
        cursor.execute(f"TRUNCATE TABLE {table_name}")

        for i, row in enumerate(rows, 1):
            row_dict = row.model_dump()

            insert_sql = f"""
            INSERT INTO {table_name}
            (glossary_term_urn, glossary_term_name, entity_urn, entity_name,
             entity_type, entity_subtype, platform, container_urn, container_name,
             domain_urn, domain_name)
            SELECT
                %(glossary_term_urn)s,
                %(glossary_term_name)s,
                %(entity_urn)s,
                %(entity_name)s,
                %(entity_type)s,
                %(entity_subtype)s,
                %(platform)s,
                %(container_urn)s,
                %(container_name)s,
                %(domain_urn)s,
                %(domain_name)s
            """

            params = row_dict

            cursor.execute(insert_sql, params)

            if i % 100 == 0:
                logger.info(f"Inserted {i}/{len(rows)} usage rows...")

        conn.commit()
        logger.info(f"Successfully inserted {len(rows)} usage rows into Snowflake")

    except Exception as e:
        logger.error(f"Error inserting usage rows to Snowflake: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()

# Copyright 2026 Acryl Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import Any, Dict, List, Optional

from datahub.ingestion.source.snowflake.snowflake_connection import (
    SnowflakeConnectionConfig,
)
from datahub_actions.action.action import Action
from datahub_actions.event.event_envelope import EventEnvelope
from datahub_actions.pipeline.pipeline_context import PipelineContext
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SnowflakeDestinationConfig(BaseModel):
    """Configuration for Snowflake destination (database, schema, table)"""

    database: str = Field(description="Target Snowflake database")
    schema_name: str = Field(description="Target Snowflake schema", alias="schema")
    table_name: str = Field(
        default="datahub_glossary_export", description="Table name to export to"
    )


class GlossaryExportConfig(BaseModel):
    """Configuration for the Glossary Export Action"""

    # Reuse DataHub's SnowflakeConnectionConfig for all auth options
    connection: SnowflakeConnectionConfig = Field(
        description="Snowflake connection configuration. Supports all DataHub Snowflake connector options including password, key pair, and OAuth authentication."
    )
    destination: SnowflakeDestinationConfig = Field(
        description="Destination database, schema, and table configuration"
    )
    export_on_startup: bool = Field(
        default=True,
        description="Whether to export glossary immediately on action startup",
    )
    batch_size: int = Field(default=1000, description="Batch size for GraphQL queries")


class GlossaryExportAction(Action):
    """
    Action to export DataHub glossary terms, nodes, and domain associations to Snowflake.

    This action exports the entire glossary structure including:
    - Glossary terms with their properties
    - Glossary node hierarchy
    - Domain associations for terms
    """

    def __init__(self, config: GlossaryExportConfig, ctx: PipelineContext):
        self.config = config
        self.ctx = ctx
        self.snowflake_conn: Any = None
        logger.info("[Config] Glossary Export to Snowflake enabled")
        logger.info(
            f"[Config] Target table: {config.destination.database}.{config.destination.schema_name}.{config.destination.table_name}"
        )

    @classmethod
    def create(cls, config_dict: dict, ctx: PipelineContext) -> "Action":
        """Factory method to create an instance of the action"""
        config = GlossaryExportConfig.model_validate(config_dict or {})
        action = cls(config, ctx)

        if config.export_on_startup:
            logger.info("Exporting glossary on startup...")
            action.export_glossary()

        return action

    def _get_snowflake_connection(self):
        """Get or create a Snowflake connection using DataHub's connection config"""
        if self.snowflake_conn is None:
            logger.info("Connecting to Snowflake...")
            # Use DataHub's get_native_connection which handles all auth types
            self.snowflake_conn = self.config.connection.get_native_connection()
            logger.info("Connected to Snowflake successfully")

            # Set the database and schema for this session
            cursor = self.snowflake_conn.cursor()
            try:
                cursor.execute(f"USE DATABASE {self.config.destination.database}")
                cursor.execute(f"USE SCHEMA {self.config.destination.schema_name}")
                logger.info(
                    f"Using database: {self.config.destination.database}, schema: {self.config.destination.schema_name}"
                )
            finally:
                cursor.close()
        return self.snowflake_conn

    def _create_table_if_not_exists(self) -> None:
        """Create the target Snowflake table if it doesn't exist"""
        conn = self._get_snowflake_connection()
        cursor = conn.cursor()

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.destination.table_name} (
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
            logger.info(f"Table {self.config.destination.table_name} created or already exists")
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise
        finally:
            cursor.close()

    def _fetch_all_glossary_terms(self) -> List[Dict[str, Any]]:
        """Fetch all glossary terms using GraphQL"""
        if self.ctx.graph is None:
            logger.error("DataHub graph client is not available")
            return []

        logger.info("Fetching all glossary terms...")

        query = """
        query searchGlossaryTerms($input: SearchInput!) {
            search(input: $input) {
                start
                count
                total
                searchResults {
                    entity {
                        urn
                        type
                        ... on GlossaryTerm {
                            name
                            hierarchicalName
                            properties {
                                name
                                description
                                definition
                                termSource
                                customProperties {
                                    key
                                    value
                                }
                                createdOn {
                                    time
                                }
                            }
                            parentNodes {
                                nodes {
                                    urn
                                    properties {
                                        name
                                    }
                                }
                            }
                            domain {
                                domain {
                                    urn
                                    properties {
                                        name
                                    }
                                }
                            }
                            ownership {
                                owners {
                                    owner {
                                        ... on CorpUser {
                                            urn
                                            type
                                            username
                                        }
                                        ... on CorpGroup {
                                            urn
                                            type
                                            name
                                        }
                                    }
                                    type
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        all_terms = []
        start = 0
        batch_size = self.config.batch_size

        while True:
            variables = {
                "input": {
                    "type": "GLOSSARY_TERM",
                    "query": "*",
                    "start": start,
                    "count": batch_size,
                }
            }

            try:
                # Access the wrapped DataHubGraph (ctx.graph is AcrylDataHubGraph, ctx.graph.graph is DataHubGraph)
                response = self.ctx.graph.graph.execute_graphql(query, variables)

                search_results = response.get("search", {})
                results = search_results.get("searchResults", [])
                total = search_results.get("total", 0)

                logger.info(f"Fetched {len(results)} terms (total: {total}, start: {start})")

                for result in results:
                    entity = result.get("entity", {})
                    if entity:
                        all_terms.append(entity)

                if len(results) == 0 or start + batch_size >= total:
                    break

                start += batch_size

            except Exception as e:
                logger.error(f"Error fetching glossary terms: {e}")
                break

        logger.info(f"Total glossary terms fetched: {len(all_terms)}")
        return all_terms

    def _fetch_all_glossary_nodes(self) -> List[Dict[str, Any]]:
        """Fetch all glossary nodes using GraphQL"""
        if self.ctx.graph is None:
            logger.error("DataHub graph client is not available")
            return []

        logger.info("Fetching all glossary nodes...")

        query = """
        query searchGlossaryNodes($input: SearchInput!) {
            search(input: $input) {
                start
                count
                total
                searchResults {
                    entity {
                        urn
                        type
                        ... on GlossaryNode {
                            properties {
                                name
                                description
                                customProperties {
                                    key
                                    value
                                }
                                createdOn {
                                    time
                                }
                            }
                            parentNodes {
                                nodes {
                                    urn
                                    properties {
                                        name
                                    }
                                }
                            }
                            ownership {
                                owners {
                                    owner {
                                        ... on CorpUser {
                                            urn
                                            type
                                            username
                                        }
                                        ... on CorpGroup {
                                            urn
                                            type
                                            name
                                        }
                                    }
                                    type
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        all_nodes = []
        start = 0
        batch_size = self.config.batch_size

        while True:
            variables = {
                "input": {
                    "type": "GLOSSARY_NODE",
                    "query": "*",
                    "start": start,
                    "count": batch_size,
                }
            }

            try:
                # Access the wrapped DataHubGraph (ctx.graph is AcrylDataHubGraph, ctx.graph.graph is DataHubGraph)
                response = self.ctx.graph.graph.execute_graphql(query, variables)

                search_results = response.get("search", {})
                results = search_results.get("searchResults", [])
                total = search_results.get("total", 0)

                logger.info(f"Fetched {len(results)} nodes (total: {total}, start: {start})")

                for result in results:
                    entity = result.get("entity", {})
                    if entity:
                        all_nodes.append(entity)

                if len(results) == 0 or start + batch_size >= total:
                    break

                start += batch_size

            except Exception as e:
                logger.error(f"Error fetching glossary nodes: {e}")
                break

        logger.info(f"Total glossary nodes fetched: {len(all_nodes)}")
        return all_nodes

    def _build_hierarchical_path(self, parent_nodes: Optional[Dict[str, Any]]) -> str:
        """Build a hierarchical path from parent nodes"""
        if not parent_nodes or not parent_nodes.get("nodes"):
            return ""

        path_parts = []
        for node in parent_nodes["nodes"]:
            node_name = node.get("properties", {}).get("name")
            if node_name:
                path_parts.append(node_name)

        return " > ".join(path_parts) if path_parts else ""

    def _transform_entity_to_row(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform a glossary entity (term or node) to a database row"""
        try:
            urn = entity.get("urn")
            entity_type = entity.get("type", "").lower()
            properties = entity.get("properties") or {}

            name = properties.get("name") if properties else None
            description = (
                (properties.get("description") or properties.get("definition"))
                if properties
                else None
            )
            created_on = properties.get("createdOn") if properties else None
            created_at = created_on.get("time") if created_on else None

            parent_nodes = entity.get("parentNodes")
            parent_node_urn = None
            parent_node_name = None
            if parent_nodes and parent_nodes.get("nodes"):
                first_parent = parent_nodes["nodes"][0]
                parent_node_urn = first_parent.get("urn")
                parent_props = first_parent.get("properties")
                parent_node_name = parent_props.get("name") if parent_props else None

            hierarchical_path = (
                entity.get("hierarchicalName")
                or self._build_hierarchical_path(parent_nodes)
                or name
            )

            domain = entity.get("domain")
            domain_info = domain.get("domain") if domain else None
            domain_urn = domain_info.get("urn") if domain_info else None
            domain_props = domain_info.get("properties") if domain_info else None
            domain_name = domain_props.get("name") if domain_props else None

            custom_properties = properties.get("customProperties", [])
            custom_props_dict = (
                {prop["key"]: prop["value"] for prop in custom_properties}
                if custom_properties
                else None
            )

            ownership = entity.get("ownership")
            ownership_info = ownership.get("owners", []) if ownership else []
            ownership_list = []
            for owner in ownership_info:
                owner_data = owner.get("owner") if owner else None
                if owner_data:
                    ownership_list.append(
                        {
                            "urn": owner_data.get("urn"),
                            "username": owner_data.get("username") or owner_data.get("name"),
                            "type": owner.get("type"),
                        }
                    )

            return {
                "urn": urn,
                "name": name,
                "entity_type": entity_type,
                "description": description,
                "parent_node_urn": parent_node_urn,
                "parent_node_name": parent_node_name,
                "hierarchical_path": hierarchical_path,
                "domain_urn": domain_urn,
                "domain_name": domain_name,
                "custom_properties": custom_props_dict,
                "ownership": ownership_list if ownership_list else None,
                "created_at": created_at,
            }

        except Exception as e:
            logger.error(f"Error transforming entity {entity.get('urn')}: {e}")
            return None

    def _insert_rows_to_snowflake(self, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into Snowflake table"""
        if not rows:
            logger.info("No rows to insert")
            return

        conn = self._get_snowflake_connection()
        cursor = conn.cursor()

        try:
            logger.info(f"Truncating table {self.config.destination.table_name}...")
            cursor.execute(f"TRUNCATE TABLE {self.config.destination.table_name}")

            import json

            # Insert rows in batches using individual execute statements
            # This avoids issues with pyformat and VARIANT columns
            for i, row in enumerate(rows, 1):
                custom_props_json = (
                    json.dumps(row["custom_properties"]) if row["custom_properties"] else None
                )
                ownership_json = json.dumps(row["ownership"]) if row["ownership"] else None

                # Use SELECT syntax which works better with function calls
                insert_sql = f"""
                INSERT INTO {self.config.destination.table_name}
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
                    "urn": row["urn"],
                    "name": row["name"],
                    "entity_type": row["entity_type"],
                    "description": row["description"],
                    "parent_node_urn": row["parent_node_urn"],
                    "parent_node_name": row["parent_node_name"],
                    "hierarchical_path": row["hierarchical_path"],
                    "domain_urn": row["domain_urn"],
                    "domain_name": row["domain_name"],
                    "custom_properties": custom_props_json,
                    "ownership": ownership_json,
                    "created_at": row["created_at"],
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

    def export_glossary(self) -> None:
        """Main method to export glossary to Snowflake"""
        try:
            logger.info("Starting glossary export...")

            self._create_table_if_not_exists()

            terms = self._fetch_all_glossary_terms()
            nodes = self._fetch_all_glossary_nodes()

            all_entities = terms + nodes
            logger.info(
                f"Total entities to export: {len(all_entities)} ({len(terms)} terms, {len(nodes)} nodes)"
            )

            rows = []
            for entity in all_entities:
                row = self._transform_entity_to_row(entity)
                if row:
                    rows.append(row)

            logger.info(f"Transformed {len(rows)} rows")

            self._insert_rows_to_snowflake(rows)

            logger.info("Glossary export completed successfully!")

        except Exception as e:
            logger.error(f"Error during glossary export: {e}", exc_info=True)
            raise

    def act(self, event: EventEnvelope) -> None:
        """
        Process events. This action primarily runs on startup,
        but can be triggered by specific events if needed.
        """
        logger.debug(f"Received event: {event.event_type}")

    def close(self) -> None:
        """Clean up resources"""
        if self.snowflake_conn:
            logger.info("Closing Snowflake connection...")
            self.snowflake_conn.close()
            self.snowflake_conn = None

"""DataHub action to export glossary terms and usage to Snowflake."""

import logging
from typing import Any

from datahub_actions.action.action import Action
from datahub_actions.event.event_envelope import EventEnvelope
from datahub_actions.pipeline.pipeline_context import PipelineContext

from .config import GlossaryExportConfig
from .graphql import (
    fetch_all_glossary_nodes,
    fetch_all_glossary_term_usage,
    fetch_all_glossary_terms,
)
from .snowflake import (
    create_glossary_table,
    create_usage_table,
    insert_glossary_rows,
    insert_usage_rows,
)
from .transformers import transform_entity_to_row, transform_usage_to_row

logger = logging.getLogger(__name__)


class GlossaryExportAction(Action):
    """Action to export DataHub glossary terms and usage to Snowflake."""

    def __init__(self, config: GlossaryExportConfig, ctx: PipelineContext):
        self.config = config
        self.ctx = ctx
        self.snowflake_conn: Any = None
        logger.info("[Config] Glossary Export to Snowflake enabled")
        logger.info(
            f"[Config] Target: {config.destination.database}.{config.destination.schema_name}.{config.destination.table_name}"
        )

    @classmethod
    def create(cls, config_dict: dict, ctx: PipelineContext) -> "Action":
        """Factory method to create an instance of the action."""
        config = GlossaryExportConfig.model_validate(config_dict or {})
        action = cls(config, ctx)

        if config.export_on_startup:
            logger.info("Exporting glossary on startup...")
            action.export_glossary()

        return action

    def _get_snowflake_connection(self):
        """Get or create a Snowflake connection."""
        if self.snowflake_conn is None:
            logger.info("Connecting to Snowflake...")
            self.snowflake_conn = self.config.connection.get_native_connection()
            logger.info("Connected to Snowflake successfully")

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

    def export_glossary(self) -> None:
        """Main method to export glossary to Snowflake."""
        try:
            logger.info("Starting glossary export...")

            conn = self._get_snowflake_connection()

            # Create tables
            create_glossary_table(conn, self.config.destination.table_name)
            create_usage_table(conn, self.config.destination.usage_table_name)

            # Fetch glossary terms and nodes
            terms = fetch_all_glossary_terms(self.ctx.graph, self.config.batch_size)
            nodes = fetch_all_glossary_nodes(self.ctx.graph, self.config.batch_size)

            all_entities = terms + nodes
            logger.info(
                f"Total entities to export: {len(all_entities)} ({len(terms)} terms, {len(nodes)} nodes)"
            )

            # Transform and insert glossary entities
            rows = []
            for entity in all_entities:
                row = transform_entity_to_row(entity)
                if row:
                    rows.append(row)

            logger.info(f"Transformed {len(rows)} glossary rows")
            insert_glossary_rows(conn, self.config.destination.table_name, rows)

            # Fetch and export glossary term usage
            logger.info("Starting glossary term usage export...")
            usage_records = fetch_all_glossary_term_usage(
                self.ctx.graph, terms, self.config.entity_types
            )

            usage_rows = []
            for usage_record in usage_records:
                usage_row = transform_usage_to_row(usage_record)
                if usage_row:
                    usage_rows.append(usage_row)

            logger.info(f"Transformed {len(usage_rows)} usage rows")
            insert_usage_rows(conn, self.config.destination.usage_table_name, usage_rows)

            logger.info("Glossary export completed successfully!")

        except Exception as e:
            logger.error(f"Error during glossary export: {e}", exc_info=True)
            raise

    def act(self, event: EventEnvelope) -> None:
        """Process events."""
        logger.debug(f"Received event: {event.event_type}")

    def close(self) -> None:
        """Clean up resources."""
        if self.snowflake_conn:
            logger.info("Closing Snowflake connection...")
            self.snowflake_conn.close()
            self.snowflake_conn = None

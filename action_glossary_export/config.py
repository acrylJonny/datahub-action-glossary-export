"""Configuration models for glossary export."""

from datahub.ingestion.source.snowflake.snowflake_connection import (
    SnowflakeConnectionConfig,
)
from pydantic import BaseModel, Field


class SnowflakeDestinationConfig(BaseModel):
    """Snowflake destination configuration."""

    database: str = Field(description="Target Snowflake database")
    schema_name: str = Field(description="Target Snowflake schema", alias="schema")
    table_name: str = Field(
        default="datahub_glossary_export", description="Table name to export to"
    )
    usage_table_name: str = Field(
        default="datahub_glossary_term_usage",
        description="Table name for glossary term usage",
    )


class GlossaryExportConfig(BaseModel):
    """Configuration for the Glossary Export Action."""

    connection: SnowflakeConnectionConfig = Field(description="Snowflake connection configuration")
    destination: SnowflakeDestinationConfig = Field(
        description="Destination database, schema, and table configuration"
    )
    export_on_startup: bool = Field(
        default=True, description="Whether to export glossary immediately on action startup"
    )
    batch_size: int = Field(default=1000, description="Batch size for GraphQL queries")
    entity_types: list[str] = Field(
        default=["DASHBOARD"],
        description="Entity types to track for glossary term usage",
    )

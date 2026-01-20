"""Data models for Snowflake rows."""

from typing import Any, Optional

from pydantic import BaseModel


class GlossaryRow(BaseModel):
    """Model for a glossary entity row in Snowflake."""

    urn: str
    name: Optional[str] = None
    entity_type: str
    description: Optional[str] = None
    parent_node_urn: Optional[str] = None
    parent_node_name: Optional[str] = None
    hierarchical_path: Optional[str] = None
    domain_urn: Optional[str] = None
    domain_name: Optional[str] = None
    custom_properties: Optional[dict[str, Any]] = None
    ownership: Optional[list[dict[str, Any]]] = None
    created_at: Optional[int] = None


class UsageRow(BaseModel):
    """Model for a glossary term usage row in Snowflake."""

    glossary_term_urn: str
    glossary_term_name: str
    entity_urn: str
    entity_name: Optional[str] = None
    entity_type: str
    entity_subtype: Optional[str] = None
    platform: Optional[str] = None
    container_urn: Optional[str] = None
    container_name: Optional[str] = None
    domain_urn: Optional[str] = None
    domain_name: Optional[str] = None

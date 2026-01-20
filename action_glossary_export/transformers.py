"""Data transformation functions."""

import logging
from typing import Any, Optional

from .models import GlossaryRow, UsageRow

logger = logging.getLogger(__name__)


def build_hierarchical_path(parent_nodes: Optional[dict[str, Any]]) -> str:
    """Build a hierarchical path from parent nodes."""
    if not parent_nodes or not parent_nodes.get("nodes"):
        return ""

    path_parts = []
    for node in parent_nodes["nodes"]:
        node_name = node.get("properties", {}).get("name")
        if node_name:
            path_parts.append(node_name)

    return " > ".join(path_parts) if path_parts else ""


def transform_entity_to_row(entity: dict[str, Any]) -> Optional[GlossaryRow]:
    """Transform a glossary entity (term or node) to a database row."""
    try:
        urn = entity.get("urn")
        if not urn:
            logger.warning("Entity missing URN, skipping")
            return None

        entity_type = entity.get("type", "").lower()
        properties = entity.get("properties") or {}

        name = properties.get("name") if properties else None
        description = (
            (properties.get("description") or properties.get("definition")) if properties else None
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
            entity.get("hierarchicalName") or build_hierarchical_path(parent_nodes) or name
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

        row_data = {
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

        return GlossaryRow.model_validate(row_data)

    except Exception as e:
        logger.error(f"Error transforming entity {entity.get('urn')}: {e}")
        return None


def transform_usage_to_row(usage_record: dict[str, Any]) -> Optional[UsageRow]:
    """Transform a glossary term usage record to a database row."""
    try:
        entity = usage_record.get("entity", {})

        entity_urn = entity.get("urn")
        if not entity_urn:
            logger.warning("Usage entity missing URN, skipping")
            return None

        glossary_term_urn = usage_record.get("glossary_term_urn")
        glossary_term_name = usage_record.get("glossary_term_name")
        if not glossary_term_urn or not glossary_term_name:
            logger.warning("Usage record missing glossary term info, skipping")
            return None

        entity_type = entity.get("type", "").lower()

        properties = entity.get("properties", {})
        entity_name = properties.get("name") if properties else None

        platform = entity.get("platform", {})
        platform_name = platform.get("name") if platform else None

        subtypes = entity.get("subTypes", {})
        type_names = subtypes.get("typeNames", []) if subtypes else []
        entity_subtype = type_names[0] if type_names else None

        container = entity.get("container", {})
        container_urn = container.get("urn") if container else None
        container_props = container.get("properties", {}) if container else {}
        container_name = container_props.get("name") if container_props else None

        domain = entity.get("domain", {})
        domain_info = domain.get("domain") if domain else None
        domain_urn = domain_info.get("urn") if domain_info else None
        domain_props = domain_info.get("properties") if domain_info else None
        domain_name = domain_props.get("name") if domain_props else None

        row_data = {
            "glossary_term_urn": glossary_term_urn,
            "glossary_term_name": glossary_term_name,
            "entity_urn": entity_urn,
            "entity_name": entity_name,
            "entity_type": entity_type,
            "entity_subtype": entity_subtype,
            "platform": platform_name,
            "container_urn": container_urn,
            "container_name": container_name,
            "domain_urn": domain_urn,
            "domain_name": domain_name,
        }

        return UsageRow.model_validate(row_data)

    except Exception as e:
        logger.error(f"Error transforming usage record: {e}")
        return None

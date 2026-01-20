"""GraphQL queries and operations."""

import logging
from typing import Any, Final

logger = logging.getLogger(__name__)

# GraphQL query constants
GLOSSARY_TERMS_QUERY: Final[str] = """
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

GLOSSARY_NODES_QUERY: Final[str] = """
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

USAGE_QUERY: Final[str] = """
query getRelatedEntities($input: SearchAcrossEntitiesInput!) {
    searchAcrossEntities(input: $input) {
        start
        count
        total
        searchResults {
            entity {
                urn
                type
                ... on Dataset {
                    name
                    properties {
                        name
                        description
                    }
                    platform {
                        name
                    }
                    subTypes {
                        typeNames
                    }
                    container {
                        urn
                        properties {
                            name
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
                }
                ... on Dashboard {
                    urn
                    properties {
                        name
                        description
                    }
                    platform {
                        name
                    }
                    subTypes {
                        typeNames
                    }
                    container {
                        urn
                        properties {
                            name
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
                }
                ... on Chart {
                    urn
                    properties {
                        name
                        description
                    }
                    platform {
                        name
                    }
                    subTypes {
                        typeNames
                    }
                    container {
                        urn
                        properties {
                            name
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
                }
                ... on DataJob {
                    urn
                    properties {
                        name
                        description
                    }
                    domain {
                        domain {
                            urn
                            properties {
                                name
                            }
                        }
                    }
                }
            }
        }
    }
}
"""


def fetch_all_glossary_terms(graph, batch_size: int) -> list[dict[str, Any]]:
    """Fetch all glossary terms using GraphQL."""
    if graph is None:
        logger.error("DataHub graph client is not available")
        return []

    logger.info("Fetching all glossary terms...")
    all_terms = []
    start = 0

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
            response = graph.graph.execute_graphql(GLOSSARY_TERMS_QUERY, variables)
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


def fetch_all_glossary_nodes(graph, batch_size: int) -> list[dict[str, Any]]:
    """Fetch all glossary nodes using GraphQL."""
    if graph is None:
        logger.error("DataHub graph client is not available")
        return []

    logger.info("Fetching all glossary nodes...")
    all_nodes = []
    start = 0

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
            response = graph.graph.execute_graphql(GLOSSARY_NODES_QUERY, variables)
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


def fetch_glossary_term_usage(
    graph, glossary_term_urn: str, entity_types: list[str]
) -> list[dict[str, Any]]:
    """Fetch entities that use a specific glossary term."""
    if graph is None:
        logger.error("DataHub graph client is not available")
        return []

    all_entities = []
    start = 0
    batch_size = 100

    while True:
        variables = {
            "input": {
                "types": entity_types,
                "query": "*",
                "start": start,
                "count": batch_size,
                "filters": [
                    {
                        "field": "glossaryTerms",
                        "values": [glossary_term_urn],
                        "condition": "EQUAL",
                    }
                ],
            },
        }

        try:
            response = graph.graph.execute_graphql(USAGE_QUERY, variables)
            search_results = response.get("searchAcrossEntities", {})
            results = search_results.get("searchResults", [])
            total = search_results.get("total", 0)

            for result in results:
                entity = result.get("entity", {})
                if entity:
                    all_entities.append(entity)

            if len(results) == 0 or start + batch_size >= total:
                break

            start += batch_size

        except Exception as e:
            logger.error(f"Error fetching usage for glossary term {glossary_term_urn}: {e}")
            break

    return all_entities


def fetch_all_glossary_term_usage(
    graph, glossary_terms: list[dict[str, Any]], entity_types: list[str]
) -> list[dict[str, Any]]:
    """Fetch usage information for all glossary terms."""
    logger.info("Fetching glossary term usage...")

    all_usage = []
    total_terms = len(glossary_terms)

    for idx, term in enumerate(glossary_terms, 1):
        term_urn = term.get("urn")
        term_name = term.get("properties", {}).get("name", "Unknown")

        if not term_urn:
            continue

        logger.info(f"Fetching usage for term {idx}/{total_terms}: {term_name}")

        entities = fetch_glossary_term_usage(graph, term_urn, entity_types)

        for entity in entities:
            usage_record = {
                "glossary_term_urn": term_urn,
                "glossary_term_name": term_name,
                "entity": entity,
            }
            all_usage.append(usage_record)

        logger.info(f"  Found {len(entities)} entities using this term")

    logger.info(f"Total usage records: {len(all_usage)}")
    return all_usage

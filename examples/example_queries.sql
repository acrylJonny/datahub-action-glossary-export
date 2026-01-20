-- Example Queries for DataHub Glossary Export
-- These queries demonstrate common use cases for analyzing the exported glossary data

-- ============================================================================
-- Basic Queries
-- ============================================================================

-- View all glossary terms
SELECT 
    name,
    description,
    hierarchical_path,
    domain_name,
    created_at
FROM glossary_export
WHERE entity_type = 'glossary_term'
ORDER BY name;

-- View all glossary nodes (folders/groups)
SELECT 
    name,
    description,
    hierarchical_path,
    parent_node_name
FROM glossary_export
WHERE entity_type = 'glossary_node'
ORDER BY hierarchical_path;

-- Count terms and nodes
SELECT 
    entity_type,
    COUNT(*) as count
FROM glossary_export
GROUP BY entity_type;

-- ============================================================================
-- Hierarchy and Structure
-- ============================================================================

-- View complete glossary hierarchy
SELECT 
    hierarchical_path,
    name,
    entity_type,
    description
FROM glossary_export
ORDER BY hierarchical_path, entity_type DESC;

-- Find all terms under a specific node
SELECT 
    name,
    description,
    hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND hierarchical_path LIKE 'Finance%'
ORDER BY hierarchical_path;

-- Find root-level terms (no parent)
SELECT 
    name,
    description,
    domain_name
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND parent_node_urn IS NULL;

-- Count terms by depth in hierarchy
SELECT 
    LENGTH(hierarchical_path) - LENGTH(REPLACE(hierarchical_path, '>', '')) as depth,
    COUNT(*) as term_count
FROM glossary_export
WHERE entity_type = 'glossary_term'
GROUP BY depth
ORDER BY depth;

-- ============================================================================
-- Domain Analysis
-- ============================================================================

-- Terms grouped by domain
SELECT 
    COALESCE(domain_name, 'No Domain') as domain,
    COUNT(*) as term_count
FROM glossary_export
WHERE entity_type = 'glossary_term'
GROUP BY domain_name
ORDER BY term_count DESC;

-- Terms without domains
SELECT 
    name,
    description,
    hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND domain_name IS NULL;

-- Domains with the most terms
SELECT 
    domain_name,
    COUNT(*) as term_count,
    LISTAGG(name, ', ') WITHIN GROUP (ORDER BY name) as sample_terms
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND domain_name IS NOT NULL
GROUP BY domain_name
ORDER BY term_count DESC
LIMIT 10;

-- ============================================================================
-- Ownership Analysis
-- ============================================================================

-- Extract ownership information (flattened)
SELECT 
    name,
    entity_type,
    o.value:urn::STRING as owner_urn,
    o.value:username::STRING as owner_username,
    o.value:type::STRING as owner_type
FROM glossary_export,
LATERAL FLATTEN(input => ownership) o
WHERE ownership IS NOT NULL
ORDER BY name;

-- Count terms by owner
SELECT 
    o.value:username::STRING as owner,
    COUNT(DISTINCT g.urn) as terms_owned
FROM glossary_export g,
LATERAL FLATTEN(input => g.ownership) o
WHERE g.entity_type = 'glossary_term'
GROUP BY owner
ORDER BY terms_owned DESC;

-- Terms without owners
SELECT 
    name,
    description,
    hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND (ownership IS NULL OR ARRAY_SIZE(ownership) = 0);

-- Owner types distribution
SELECT 
    o.value:type::STRING as owner_type,
    COUNT(*) as count
FROM glossary_export,
LATERAL FLATTEN(input => ownership) o
WHERE ownership IS NOT NULL
GROUP BY owner_type;

-- ============================================================================
-- Custom Properties Analysis
-- ============================================================================

-- View custom properties for all terms
SELECT 
    name,
    custom_properties
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND custom_properties IS NOT NULL;

-- Extract specific custom property
SELECT 
    name,
    custom_properties:data_classification::STRING as data_classification,
    custom_properties:business_criticality::STRING as business_criticality
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND custom_properties IS NOT NULL;

-- Find terms with specific custom property
SELECT 
    name,
    description,
    custom_properties
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND custom_properties:data_classification::STRING = 'PII';

-- ============================================================================
-- Search and Discovery
-- ============================================================================

-- Full-text search in names and descriptions
SELECT 
    name,
    description,
    hierarchical_path,
    entity_type
FROM glossary_export
WHERE LOWER(name) LIKE '%revenue%'
    OR LOWER(description) LIKE '%revenue%'
ORDER BY entity_type, name;

-- Find terms by partial name match
SELECT 
    name,
    description,
    hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND LOWER(name) LIKE '%customer%'
ORDER BY name;

-- Recently created terms
SELECT 
    name,
    description,
    created_at,
    hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND created_at IS NOT NULL
ORDER BY created_at DESC
LIMIT 20;

-- ============================================================================
-- Data Quality Checks
-- ============================================================================

-- Terms without descriptions
SELECT 
    name,
    hierarchical_path,
    domain_name
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND (description IS NULL OR LENGTH(TRIM(description)) = 0);

-- Short descriptions (potential incomplete definitions)
SELECT 
    name,
    description,
    LENGTH(description) as desc_length
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND description IS NOT NULL
    AND LENGTH(description) < 50
ORDER BY desc_length;

-- Terms with long hierarchical paths (deeply nested)
SELECT 
    name,
    hierarchical_path,
    LENGTH(hierarchical_path) - LENGTH(REPLACE(hierarchical_path, '>', '')) as depth
FROM glossary_export
WHERE entity_type = 'glossary_term'
HAVING depth > 5
ORDER BY depth DESC;

-- ============================================================================
-- Reporting and Dashboards
-- ============================================================================

-- Executive summary
SELECT 
    'Total Terms' as metric,
    COUNT(*) as value
FROM glossary_export
WHERE entity_type = 'glossary_term'
UNION ALL
SELECT 
    'Total Nodes' as metric,
    COUNT(*) as value
FROM glossary_export
WHERE entity_type = 'glossary_node'
UNION ALL
SELECT 
    'Terms with Domains' as metric,
    COUNT(*) as value
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND domain_name IS NOT NULL
UNION ALL
SELECT 
    'Terms with Owners' as metric,
    COUNT(*) as value
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND ownership IS NOT NULL
UNION ALL
SELECT 
    'Terms with Descriptions' as metric,
    COUNT(*) as value
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND description IS NOT NULL;

-- Domain coverage report
SELECT 
    domain_name,
    COUNT(*) as term_count,
    COUNT(CASE WHEN description IS NOT NULL THEN 1 END) as terms_with_desc,
    COUNT(CASE WHEN ownership IS NOT NULL THEN 1 END) as terms_with_owners,
    ROUND(COUNT(CASE WHEN description IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as pct_with_desc,
    ROUND(COUNT(CASE WHEN ownership IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as pct_with_owners
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND domain_name IS NOT NULL
GROUP BY domain_name
ORDER BY term_count DESC;

-- Glossary completeness scorecard
WITH metrics AS (
    SELECT 
        COUNT(*) as total_terms,
        COUNT(CASE WHEN description IS NOT NULL AND LENGTH(description) > 50 THEN 1 END) as good_descriptions,
        COUNT(CASE WHEN domain_name IS NOT NULL THEN 1 END) as has_domain,
        COUNT(CASE WHEN ownership IS NOT NULL THEN 1 END) as has_owner,
        COUNT(CASE WHEN custom_properties IS NOT NULL THEN 1 END) as has_custom_props
    FROM glossary_export
    WHERE entity_type = 'glossary_term'
)
SELECT 
    total_terms,
    good_descriptions,
    ROUND(good_descriptions * 100.0 / NULLIF(total_terms, 0), 2) as pct_good_descriptions,
    has_domain,
    ROUND(has_domain * 100.0 / NULLIF(total_terms, 0), 2) as pct_with_domain,
    has_owner,
    ROUND(has_owner * 100.0 / NULLIF(total_terms, 0), 2) as pct_with_owner,
    ROUND((good_descriptions + has_domain + has_owner) * 100.0 / (total_terms * 3), 2) as overall_completeness_score
FROM metrics;

-- ============================================================================
-- Export for Other Tools
-- ============================================================================

-- Export as simple list (for documentation)
SELECT 
    hierarchical_path || ' - ' || name as term_full_name,
    description
FROM glossary_export
WHERE entity_type = 'glossary_term'
ORDER BY hierarchical_path;

-- Export term-to-domain mapping (for integration)
SELECT 
    urn as term_urn,
    name as term_name,
    domain_urn,
    domain_name
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND domain_urn IS NOT NULL;

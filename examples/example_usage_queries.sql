-- Example SQL queries for analyzing glossary term usage
-- Author: Jonny Dixon
-- Date: January 20, 2026

-- ============================================================================
-- BASIC QUERIES
-- ============================================================================

-- Get all Power BI reports using glossary terms
SELECT 
    glossary_term_name,
    entity_name as report_name,
    entity_subtype,
    container_name as workspace_name,
    domain_name
FROM glossary_term_usage
WHERE platform = 'powerbi'
    AND entity_type = 'dashboard'
ORDER BY glossary_term_name, entity_name;

-- Get all Tableau dashboards using glossary terms
SELECT 
    glossary_term_name,
    entity_name as dashboard_name,
    container_name as workbook_name,
    domain_name
FROM glossary_term_usage
WHERE platform = 'tableau'
    AND entity_type = 'dashboard'
ORDER BY glossary_term_name, entity_name;

-- Find which glossary terms are used in a specific report
SELECT 
    u.glossary_term_name,
    g.hierarchical_path,
    g.description
FROM glossary_term_usage u
JOIN glossary_export g ON u.glossary_term_urn = g.urn
WHERE u.entity_name = 'Sales Dashboard'
ORDER BY g.hierarchical_path;

-- ============================================================================
-- USAGE STATISTICS
-- ============================================================================

-- Get usage statistics by glossary term
SELECT 
    g.name as term_name,
    g.hierarchical_path,
    COUNT(DISTINCT u.entity_urn) as total_usage_count,
    COUNT(DISTINCT CASE WHEN u.entity_type = 'dashboard' THEN u.entity_urn END) as dashboard_count,
    COUNT(DISTINCT CASE WHEN u.entity_type = 'chart' THEN u.entity_urn END) as chart_count,
    COUNT(DISTINCT CASE WHEN u.entity_type = 'dataset' THEN u.entity_urn END) as dataset_count,
    COUNT(DISTINCT CASE WHEN u.entity_type = 'datajob' THEN u.entity_urn END) as datajob_count,
    COUNT(DISTINCT u.platform) as platform_count,
    LISTAGG(DISTINCT u.platform, ', ') WITHIN GROUP (ORDER BY u.platform) as platforms
FROM glossary_export g
LEFT JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
WHERE g.entity_type = 'glossary_term'
GROUP BY g.name, g.hierarchical_path
ORDER BY total_usage_count DESC;

-- Top 10 most used glossary terms
SELECT 
    g.name as term_name,
    g.hierarchical_path,
    COUNT(DISTINCT u.entity_urn) as usage_count
FROM glossary_export g
INNER JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
WHERE g.entity_type = 'glossary_term'
GROUP BY g.name, g.hierarchical_path
ORDER BY usage_count DESC
LIMIT 10;

-- Find glossary terms NOT being used anywhere
SELECT 
    name as unused_term,
    hierarchical_path,
    domain_name,
    created_at
FROM glossary_export g
WHERE entity_type = 'glossary_term'
    AND NOT EXISTS (
        SELECT 1 
        FROM glossary_term_usage u 
        WHERE u.glossary_term_urn = g.urn
    )
ORDER BY hierarchical_path;

-- ============================================================================
-- DOMAIN ANALYSIS
-- ============================================================================

-- Get all entities in a domain using specific glossary terms
SELECT 
    u.glossary_term_name,
    u.entity_name,
    u.entity_type,
    u.entity_subtype,
    u.platform,
    u.domain_name
FROM glossary_term_usage u
WHERE u.domain_name = 'Sales Domain'
ORDER BY u.glossary_term_name, u.entity_type, u.entity_name;

-- Count glossary term usage by domain
SELECT 
    u.domain_name,
    COUNT(DISTINCT u.glossary_term_urn) as unique_terms_used,
    COUNT(DISTINCT u.entity_urn) as total_entities_using_terms,
    COUNT(DISTINCT CASE WHEN u.entity_type = 'dashboard' THEN u.entity_urn END) as dashboards
FROM glossary_term_usage u
WHERE u.domain_name IS NOT NULL
GROUP BY u.domain_name
ORDER BY total_entities_using_terms DESC;

-- ============================================================================
-- PLATFORM ANALYSIS
-- ============================================================================

-- Count glossary term usage by platform
SELECT 
    platform,
    COUNT(DISTINCT glossary_term_urn) as unique_terms_used,
    COUNT(DISTINCT entity_urn) as total_entities,
    COUNT(DISTINCT CASE WHEN entity_type = 'dashboard' THEN entity_urn END) as dashboards,
    COUNT(DISTINCT CASE WHEN entity_type = 'chart' THEN entity_urn END) as charts,
    COUNT(DISTINCT CASE WHEN entity_type = 'dataset' THEN entity_urn END) as datasets
FROM glossary_term_usage
WHERE platform IS NOT NULL
GROUP BY platform
ORDER BY total_entities DESC;

-- ============================================================================
-- CROSS-PLATFORM USAGE
-- ============================================================================

-- Find glossary terms used across multiple platforms
SELECT 
    glossary_term_name,
    COUNT(DISTINCT platform) as platform_count,
    LISTAGG(DISTINCT platform, ', ') WITHIN GROUP (ORDER BY platform) as platforms,
    COUNT(DISTINCT entity_urn) as total_entities
FROM glossary_term_usage
GROUP BY glossary_term_name
HAVING COUNT(DISTINCT platform) > 1
ORDER BY platform_count DESC, total_entities DESC;

-- ============================================================================
-- LINEAGE AND IMPACT ANALYSIS
-- ============================================================================

-- Find all reports and datasets using a specific glossary term (impact analysis)
SELECT 
    u.entity_type,
    u.entity_name,
    u.platform,
    u.entity_subtype,
    u.container_name,
    u.domain_name
FROM glossary_term_usage u
WHERE u.glossary_term_name = 'Revenue'
ORDER BY u.entity_type, u.platform, u.entity_name;

-- Find all glossary terms used in a specific workspace/container
SELECT 
    u.glossary_term_name,
    g.hierarchical_path,
    COUNT(DISTINCT u.entity_urn) as entity_count
FROM glossary_term_usage u
JOIN glossary_export g ON u.glossary_term_urn = g.urn
WHERE u.container_name = 'Sales Workspace'
GROUP BY u.glossary_term_name, g.hierarchical_path
ORDER BY entity_count DESC;

-- ============================================================================
-- QUALITY & GOVERNANCE
-- ============================================================================

-- Find reports without domain assignment that use glossary terms
SELECT 
    u.entity_name,
    u.platform,
    u.entity_type,
    COUNT(DISTINCT u.glossary_term_urn) as terms_used
FROM glossary_term_usage u
WHERE u.domain_name IS NULL
GROUP BY u.entity_name, u.platform, u.entity_type
ORDER BY terms_used DESC;

-- Find entities using glossary terms from different domains (potential governance issue)
SELECT 
    u.entity_name,
    u.entity_type,
    u.platform,
    u.domain_name as entity_domain,
    COUNT(DISTINCT g.domain_name) as unique_term_domains,
    LISTAGG(DISTINCT g.domain_name, ', ') WITHIN GROUP (ORDER BY g.domain_name) as term_domains
FROM glossary_term_usage u
JOIN glossary_export g ON u.glossary_term_urn = g.urn
GROUP BY u.entity_name, u.entity_type, u.platform, u.domain_name
HAVING COUNT(DISTINCT g.domain_name) > 1
    OR (u.domain_name IS NOT NULL AND MAX(g.domain_name) != u.domain_name)
ORDER BY unique_term_domains DESC;

-- ============================================================================
-- HIERARCHICAL ANALYSIS
-- ============================================================================

-- Find usage by glossary term hierarchy (top-level category)
SELECT 
    SPLIT_PART(g.hierarchical_path, ' > ', 1) as top_level_category,
    COUNT(DISTINCT g.urn) as terms_in_category,
    COUNT(DISTINCT u.entity_urn) as total_entity_usage
FROM glossary_export g
LEFT JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
WHERE g.entity_type = 'glossary_term'
GROUP BY SPLIT_PART(g.hierarchical_path, ' > ', 1)
ORDER BY total_entity_usage DESC;

-- ============================================================================
-- TIME-BASED ANALYSIS
-- ============================================================================

-- Recently created glossary terms and their adoption
SELECT 
    g.name as term_name,
    g.created_at,
    DATEDIFF(day, g.created_at, CURRENT_TIMESTAMP()) as days_since_creation,
    COUNT(DISTINCT u.entity_urn) as usage_count
FROM glossary_export g
LEFT JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
WHERE g.entity_type = 'glossary_term'
    AND g.created_at >= DATEADD(day, -90, CURRENT_TIMESTAMP())
GROUP BY g.name, g.created_at
ORDER BY g.created_at DESC;

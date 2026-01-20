# Glossary Term Usage Tracking Guide

**Author**: Jonny Dixon  
**Date**: January 20, 2026

## Overview

This guide explains the new **Glossary Term Usage** feature that tracks where glossary terms are used across your data ecosystem, including Power BI reports, Tableau dashboards, Snowflake tables, and other data assets.

## What's New

The action now creates **two tables** in Snowflake:

1. **Glossary Export Table** (default: `datahub_glossary_export`) - Contains glossary terms and nodes
2. **Glossary Term Usage Table** (default: `datahub_glossary_term_usage`) - Tracks where each term is used

## Benefits

### 1. **Impact Analysis**
- Understand which reports and dashboards will be affected if you change a glossary term
- See the downstream impact of term definitions on your data assets

### 2. **Adoption Tracking**
- Identify which glossary terms are heavily used vs. underutilized
- Find unused terms that may need promotion or retirement

### 3. **Governance & Quality**
- Ensure reports are properly tagged with relevant business terminology
- Find reports using terms from multiple domains (potential governance issue)
- Identify reports without proper domain assignments

### 4. **Cross-Platform Visibility**
- See which terms are used across Power BI, Tableau, Snowflake, and other platforms
- Track term adoption by platform

## Configuration

Configure the usage tracking in your action configuration:

```yaml
destination:
  database: "DATAHUB"
  schema: "METADATA"
  table_name: "glossary_export"
  usage_table_name: "glossary_term_usage"

entity_types:  # Entity types to track (default: ["DASHBOARD"])
  - DASHBOARD  # Power BI reports, Tableau dashboards
  # - CHART     # Uncomment to track individual visualizations
  # - DATASET   # Uncomment to track tables and views
  # - DATA_JOB  # Uncomment to track dbt models and pipelines
```

**Note**: By default, only dashboards/reports are tracked. This keeps the export fast and focused on the most common use case (Power BI/Tableau reports). Add other entity types if you need to track datasets or pipelines.

## Usage Table Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `glossary_term_urn` | VARCHAR(500) | Glossary term URN | `urn:li:glossaryTerm:revenue` |
| `glossary_term_name` | VARCHAR(500) | Glossary term name | "Revenue" |
| `entity_urn` | VARCHAR(500) | Entity using the term | `urn:li:dashboard:(powerbi,sales-dashboard)` |
| `entity_name` | VARCHAR(500) | Entity name | "Sales Dashboard" |
| `entity_type` | VARCHAR(50) | Type of entity | dashboard, chart, dataset, datajob |
| `entity_subtype` | VARCHAR(100) | Platform-specific subtype | Report, Table, View |
| `platform` | VARCHAR(100) | Source platform | powerbi, tableau, snowflake |
| `container_urn` | VARCHAR(500) | Parent container URN | Workspace or schema URN |
| `container_name` | VARCHAR(500) | Parent container name | "Sales Workspace" |
| `domain_urn` | VARCHAR(500) | Associated domain URN | `urn:li:domain:sales` |
| `domain_name` | VARCHAR(500) | Associated domain name | "Sales Domain" |
| `last_updated` | TIMESTAMP_NTZ | Last update timestamp | Auto-updated |

## Common Use Cases

### Use Case 1: Find All Power BI Reports Using a Glossary Term

**Scenario**: You want to see which Power BI reports use the "Revenue" term.

```sql
SELECT 
    entity_name as report_name,
    container_name as workspace_name,
    domain_name
FROM glossary_term_usage
WHERE glossary_term_name = 'Revenue'
    AND platform = 'powerbi'
    AND entity_type = 'dashboard'
ORDER BY workspace_name, report_name;
```

### Use Case 2: Impact Analysis - What Will Be Affected If I Change This Term?

**Scenario**: You're considering updating the definition of "Customer Lifetime Value" and need to know what will be impacted.

```sql
SELECT 
    entity_type,
    platform,
    entity_name,
    container_name,
    domain_name
FROM glossary_term_usage
WHERE glossary_term_name = 'Customer Lifetime Value'
ORDER BY entity_type, platform, entity_name;
```

**Output Example**:
```
ENTITY_TYPE  | PLATFORM  | ENTITY_NAME           | CONTAINER_NAME     | DOMAIN_NAME
-------------|-----------|----------------------|--------------------|--------------
chart        | powerbi   | CLV Trend Chart      | Analytics Workspace| Sales Domain
dashboard    | powerbi   | Customer Dashboard   | Sales Workspace    | Sales Domain
dashboard    | tableau   | Executive Overview   | Finance Workbook   | Finance Domain
dataset      | snowflake | customer_metrics     | analytics_schema   | Analytics
```

### Use Case 3: Find Unused Glossary Terms

**Scenario**: Identify glossary terms that aren't being used anywhere.

```sql
SELECT 
    g.name as unused_term,
    g.hierarchical_path,
    g.domain_name,
    g.created_at
FROM glossary_export g
WHERE g.entity_type = 'glossary_term'
    AND NOT EXISTS (
        SELECT 1 
        FROM glossary_term_usage u 
        WHERE u.glossary_term_urn = g.urn
    )
ORDER BY g.created_at DESC;
```

### Use Case 4: Top 10 Most Used Terms

**Scenario**: See which glossary terms have the highest adoption.

```sql
SELECT 
    g.name as term_name,
    g.hierarchical_path,
    COUNT(DISTINCT u.entity_urn) as usage_count,
    COUNT(DISTINCT u.platform) as platform_count
FROM glossary_export g
INNER JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
WHERE g.entity_type = 'glossary_term'
GROUP BY g.name, g.hierarchical_path
ORDER BY usage_count DESC
LIMIT 10;
```

### Use Case 5: Governance Check - Reports Using Terms from Different Domains

**Scenario**: Find reports that use glossary terms from multiple domains, which might indicate governance issues.

```sql
SELECT 
    u.entity_name,
    u.platform,
    u.domain_name as report_domain,
    COUNT(DISTINCT g.domain_name) as unique_term_domains,
    LISTAGG(DISTINCT g.domain_name || ': ' || g.name, '; ') 
        WITHIN GROUP (ORDER BY g.domain_name) as terms_by_domain
FROM glossary_term_usage u
JOIN glossary_export g ON u.glossary_term_urn = g.urn
GROUP BY u.entity_name, u.platform, u.domain_name
HAVING COUNT(DISTINCT g.domain_name) > 1
ORDER BY unique_term_domains DESC;
```

### Use Case 6: Platform Adoption Analysis

**Scenario**: See which platforms are most actively using glossary terms.

```sql
SELECT 
    platform,
    COUNT(DISTINCT glossary_term_urn) as unique_terms_used,
    COUNT(DISTINCT entity_urn) as total_entities,
    COUNT(DISTINCT CASE WHEN entity_type = 'dashboard' THEN entity_urn END) as dashboards,
    COUNT(DISTINCT CASE WHEN entity_type = 'dataset' THEN entity_urn END) as datasets
FROM glossary_term_usage
WHERE platform IS NOT NULL
GROUP BY platform
ORDER BY total_entities DESC;
```

### Use Case 7: Workspace/Container Analysis

**Scenario**: See which glossary terms are used in a specific Power BI workspace.

```sql
SELECT 
    u.glossary_term_name,
    g.hierarchical_path,
    g.description,
    COUNT(DISTINCT u.entity_urn) as entity_count
FROM glossary_term_usage u
JOIN glossary_export g ON u.glossary_term_urn = g.urn
WHERE u.container_name = 'Sales Workspace'
    AND u.platform = 'powerbi'
GROUP BY u.glossary_term_name, g.hierarchical_path, g.description
ORDER BY entity_count DESC;
```

### Use Case 8: Term Adoption Over Time

**Scenario**: Track how recently created terms are being adopted.

```sql
SELECT 
    g.name as term_name,
    g.created_at,
    DATEDIFF(day, g.created_at, CURRENT_TIMESTAMP()) as days_since_creation,
    COUNT(DISTINCT u.entity_urn) as usage_count,
    CASE 
        WHEN COUNT(DISTINCT u.entity_urn) = 0 THEN 'Not Used'
        WHEN COUNT(DISTINCT u.entity_urn) < 5 THEN 'Low Adoption'
        WHEN COUNT(DISTINCT u.entity_urn) < 20 THEN 'Medium Adoption'
        ELSE 'High Adoption'
    END as adoption_level
FROM glossary_export g
LEFT JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
WHERE g.entity_type = 'glossary_term'
    AND g.created_at >= DATEADD(day, -90, CURRENT_TIMESTAMP())
GROUP BY g.name, g.created_at
ORDER BY g.created_at DESC;
```

## Supported Entity Types

The usage tracking supports the following entity types:

| Entity Type | Description | Examples |
|-------------|-------------|----------|
| `dashboard` | BI dashboards and reports | Power BI reports, Tableau dashboards, Looker dashboards |
| `chart` | Individual visualizations | Power BI visuals, Tableau worksheets |
| `dataset` | Tables, views, and datasets | Snowflake tables, BigQuery datasets |
| `datajob` | Data pipelines and transformations | dbt models, Airflow DAGs |

## Supported Platforms

Common platforms that will appear in the usage data:

- **powerbi** - Microsoft Power BI
- **tableau** - Tableau
- **looker** - Looker
- **snowflake** - Snowflake
- **bigquery** - Google BigQuery
- **redshift** - Amazon Redshift
- **databricks** - Databricks
- **dbt** - dbt transformations

## Technical Details

### How It Works

1. **Glossary Export**: First, the action exports all glossary terms and nodes
2. **Usage Query**: For each glossary term, the action queries DataHub using GraphQL to find entities that have that term tagged
3. **Data Transformation**: The entity information is transformed into usage records
4. **Snowflake Insert**: All usage records are inserted into the usage table

### Performance Considerations

- The usage export runs sequentially for each glossary term
- For large glossaries (100+ terms), the export may take several minutes
- The action uses batch size configuration (default: 1000) for pagination

### GraphQL Query

The action uses the `searchAcrossEntities` GraphQL query with a glossary term filter:

```graphql
query getRelatedEntities($urn: String!, $input: SearchAcrossEntitiesInput!) {
  searchAcrossEntities(input: $input) {
    searchResults {
      entity {
        urn
        type
        ... on Dashboard {
          properties { name description }
          platform { name }
          subTypes { typeNames }
          container { ... }
          domain { ... }
        }
        # Similar fragments for Chart, Dataset, DataJob
      }
    }
  }
}
```

## Monitoring and Troubleshooting

### Check Export Progress

Monitor the action logs to see progress:

```
[INFO] Fetching usage for term 1/50: Revenue
[INFO]   Found 5 entities using this term
[INFO] Fetching usage for term 2/50: Customer
[INFO]   Found 12 entities using this term
...
[INFO] Total usage records: 287
[INFO] Transformed 287 usage rows
[INFO] Successfully inserted 287 usage rows into Snowflake
```

### No Usage Data

If no usage records are found:

1. **Check if entities are tagged**: Verify in DataHub UI that reports/dashboards have glossary terms applied
2. **Verify permissions**: Ensure the DataHub token has read access to all entity types
3. **Check platform coverage**: Some platforms may not support glossary term tagging

### Performance Optimization

For large glossaries (500+ terms):

1. Consider running during off-hours
2. Monitor the batch_size configuration
3. Check Snowflake warehouse size if inserts are slow

## Example Dashboards

### Usage Summary Dashboard

Create a summary view for executives:

```sql
CREATE OR REPLACE VIEW glossary_usage_summary AS
SELECT 
    COUNT(DISTINCT g.urn) as total_terms,
    COUNT(DISTINCT CASE WHEN u.entity_urn IS NOT NULL THEN g.urn END) as used_terms,
    COUNT(DISTINCT u.entity_urn) as total_entities_using_terms,
    COUNT(DISTINCT CASE WHEN u.entity_type = 'dashboard' THEN u.entity_urn END) as dashboards,
    COUNT(DISTINCT CASE WHEN u.entity_type = 'dataset' THEN u.entity_urn END) as datasets,
    COUNT(DISTINCT u.platform) as platforms
FROM glossary_export g
LEFT JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
WHERE g.entity_type = 'glossary_term';
```

### Term Detail View

Create a detailed view for a specific term:

```sql
CREATE OR REPLACE VIEW revenue_term_usage AS
SELECT 
    u.entity_type,
    u.platform,
    u.entity_name,
    u.entity_subtype,
    u.container_name,
    u.domain_name,
    u.last_updated
FROM glossary_term_usage u
WHERE u.glossary_term_name = 'Revenue'
ORDER BY u.entity_type, u.platform, u.entity_name;
```

## Advanced Queries

See [example_usage_queries.sql](../example_usage_queries.sql) for a comprehensive set of example queries including:

- Cross-platform usage analysis
- Hierarchical analysis by glossary category
- Quality and governance checks
- Time-based adoption tracking
- Impact analysis queries

## Next Steps

1. **Run the updated action** to populate the usage table
2. **Explore the data** using the example queries
3. **Create dashboards** in your BI tool to visualize term usage
4. **Set up alerts** for governance issues (e.g., terms from wrong domains)
5. **Track adoption** over time to measure glossary success

## Support

For questions or issues:
- Check the main [README](../README.md) for general action configuration
- Review [example_usage_queries.sql](../example_usage_queries.sql) for query examples
- See [Quick Start Guide](QUICKSTART_USAGE.md) for getting started
- Open an issue on GitHub

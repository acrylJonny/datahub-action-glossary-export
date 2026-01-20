# Examples

This directory contains example configurations and SQL queries to help you get started.

## Configuration Files

### example_action.yaml
Complete action configuration example for DataHub Actions framework.

**Usage:**
1. Copy to your deployment location
2. Update the Snowflake connection settings
3. Set environment variables for sensitive values
4. Run with: `datahub actions -c example_action.yaml`

**See also:** [DEPLOYMENT.md](../DEPLOYMENT.md) for deployment instructions

### local_config.yaml
Configuration example for local development and testing.

**Usage:**
1. Copy to your working directory
2. Update with your local Snowflake and DataHub credentials
3. Test locally before deploying

**See also:** [LOCAL_EXECUTION.md](../LOCAL_EXECUTION.md) for local development

## SQL Query Examples

### example_queries.sql
Example SQL queries for analyzing the **glossary export** data (terms, nodes, hierarchy, domains, ownership).

**Includes queries for:**
- Basic glossary browsing
- Hierarchy and structure analysis
- Domain analysis
- Ownership analysis
- Custom properties exploration
- Search and discovery
- Data quality checks
- Reporting and dashboards

**350+ lines** of production-ready SQL examples

### example_usage_queries.sql
Example SQL queries for analyzing **glossary term usage** in reports and dashboards.

**Includes queries for:**
- Basic usage queries (Power BI, Tableau, etc.)
- Usage statistics and adoption metrics
- Domain analysis
- Platform analysis
- Cross-platform usage
- Impact analysis
- Quality and governance checks
- Hierarchical analysis
- Time-based analysis

**230+ lines** of production-ready SQL examples

## Quick Start

### 1. Deploy the Action

```bash
# Copy example config
cp examples/example_action.yaml my_action.yaml

# Edit with your settings
vi my_action.yaml

# Deploy
datahub actions -c my_action.yaml
```

### 2. Query the Data

Once the action runs, use the example SQL queries:

```sql
-- Copy queries from examples/example_queries.sql
-- Run in your Snowflake console or BI tool

-- Example: View all glossary terms
SELECT name, description, hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
ORDER BY hierarchical_path;

-- Example: See most-used glossary terms
SELECT 
    g.name,
    COUNT(DISTINCT u.entity_urn) as usage_count
FROM glossary_export g
JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
GROUP BY g.name
ORDER BY usage_count DESC;
```

## See Also

- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [docs/GLOSSARY_USAGE_GUIDE.md](../docs/GLOSSARY_USAGE_GUIDE.md) - Detailed usage guide
- [docs/QUICKSTART_USAGE.md](../docs/QUICKSTART_USAGE.md) - Quick start with examples
- [SNOWFLAKE_SETUP.md](../SNOWFLAKE_SETUP.md) - Snowflake setup instructions

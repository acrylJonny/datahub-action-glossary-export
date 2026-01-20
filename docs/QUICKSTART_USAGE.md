# Quick Start: Glossary Term Usage Tracking

**Get started with glossary term usage tracking in 5 minutes!**

## What You'll Get

After following this guide, you'll be able to answer questions like:

- **Which Power BI reports use the "Revenue" term?**
- **What will be impacted if I change this glossary term?**
- **Which glossary terms are being adopted vs. ignored?**
- **Are my reports using terms from the right domains?**

## Step 1: Update Your Configuration (Optional)

Your existing configuration already works! But you can customize:

```yaml
destination:
  database: "DATAHUB"
  schema: "METADATA"
  table_name: "glossary_export"
  usage_table_name: "glossary_term_usage"  # Optional (default: datahub_glossary_term_usage)

entity_types:  # Optional (default: ["DASHBOARD"] - only Power BI/Tableau reports)
  - DASHBOARD
  # - CHART     # Uncomment to also track charts
  # - DATASET   # Uncomment to also track tables/views
  # - DATA_JOB  # Uncomment to also track pipelines
```

**Defaults**: 
- `usage_table_name`: `datahub_glossary_term_usage`
- `entity_types`: `["DASHBOARD"]` (tracks only dashboards/reports for faster exports)

## Step 2: Run the Action

```bash
datahub actions -c action.yaml
```

**What happens?**

1. Creates two tables: `glossary_export` and `glossary_term_usage`
2. Exports all glossary terms and nodes
3. For each term, finds where it's used (Power BI, Tableau, datasets, etc.)
4. Inserts all usage records into Snowflake

**Expected output:**

```
[INFO] Starting glossary export...
[INFO] Table glossary_export created or already exists
[INFO] Table glossary_term_usage created or already exists
[INFO] Fetching all glossary terms...
[INFO] Total glossary terms fetched: 50
[INFO] Starting glossary term usage export...
[INFO] Fetching usage for term 1/50: Revenue
[INFO]   Found 5 entities using this term
[INFO] Fetching usage for term 2/50: Profit
[INFO]   Found 3 entities using this term
...
[INFO] Total usage records: 287
[INFO] Successfully inserted 287 usage rows into Snowflake
[INFO] Glossary export completed successfully!
```

## Step 3: Query Your Data

### Quick Check

```sql
-- See what data was exported
SELECT COUNT(*) FROM glossary_term_usage;

-- See a few examples
SELECT 
    glossary_term_name,
    entity_name,
    entity_type,
    platform
FROM glossary_term_usage
LIMIT 10;
```

### Common Queries

#### 1. Which Power BI Reports Use a Specific Term?

```sql
SELECT 
    entity_name as report_name,
    container_name as workspace_name
FROM glossary_term_usage
WHERE glossary_term_name = 'Revenue'
    AND platform = 'powerbi'
    AND entity_type = 'dashboard'
ORDER BY workspace_name, report_name;
```

#### 2. What Will Be Impacted If I Change This Term?

```sql
SELECT 
    entity_type,
    platform,
    COUNT(*) as count
FROM glossary_term_usage
WHERE glossary_term_name = 'Customer Lifetime Value'
GROUP BY entity_type, platform
ORDER BY count DESC;
```

**Example output:**
```
ENTITY_TYPE  | PLATFORM  | COUNT
-------------|-----------|------
dashboard    | powerbi   | 12
dataset      | snowflake | 8
chart        | tableau   | 5
```

#### 3. Top 10 Most Used Terms

```sql
SELECT 
    glossary_term_name,
    COUNT(*) as usage_count,
    COUNT(DISTINCT platform) as platform_count
FROM glossary_term_usage
GROUP BY glossary_term_name
ORDER BY usage_count DESC
LIMIT 10;
```

#### 4. Find Unused Terms

```sql
SELECT 
    g.name as unused_term,
    g.hierarchical_path
FROM glossary_export g
WHERE g.entity_type = 'glossary_term'
    AND NOT EXISTS (
        SELECT 1 FROM glossary_term_usage u 
        WHERE u.glossary_term_urn = g.urn
    )
ORDER BY g.hierarchical_path;
```

#### 5. Platform Adoption

```sql
SELECT 
    platform,
    COUNT(DISTINCT glossary_term_urn) as terms_used,
    COUNT(*) as total_usage
FROM glossary_term_usage
GROUP BY platform
ORDER BY total_usage DESC;
```

## Step 4: Create a Dashboard

Copy any of the queries above into your BI tool (Power BI, Tableau, Looker, etc.) to create visualizations.

### Recommended Visualizations

1. **Bar Chart**: Top 10 most used terms
2. **Table**: Impact analysis for a specific term
3. **Treemap**: Usage by platform and entity type
4. **KPI Cards**: 
   - Total terms
   - Total usage records
   - Number of platforms
   - Unused terms count

## Real-World Examples

### Example 1: Power BI Report Audit

**Question**: "Which Power BI reports in the Sales workspace use glossary terms?"

```sql
SELECT 
    u.glossary_term_name,
    u.entity_name as report_name,
    g.description as term_definition
FROM glossary_term_usage u
JOIN glossary_export g ON u.glossary_term_urn = g.urn
WHERE u.platform = 'powerbi'
    AND u.container_name = 'Sales Workspace'
ORDER BY u.entity_name, u.glossary_term_name;
```

### Example 2: Cross-Domain Governance Check

**Question**: "Are there reports using terms from multiple domains?"

```sql
SELECT 
    u.entity_name,
    u.platform,
    u.domain_name as report_domain,
    COUNT(DISTINCT g.domain_name) as term_domains,
    LISTAGG(DISTINCT g.domain_name, ', ') as domains
FROM glossary_term_usage u
JOIN glossary_export g ON u.glossary_term_urn = g.urn
GROUP BY u.entity_name, u.platform, u.domain_name
HAVING COUNT(DISTINCT g.domain_name) > 1
ORDER BY term_domains DESC;
```

### Example 3: Term Adoption Tracking

**Question**: "How are our glossary terms being adopted?"

```sql
SELECT 
    CASE 
        WHEN usage_count = 0 THEN 'Not Used'
        WHEN usage_count < 5 THEN 'Low (1-4)'
        WHEN usage_count < 20 THEN 'Medium (5-19)'
        ELSE 'High (20+)'
    END as adoption_level,
    COUNT(*) as term_count
FROM (
    SELECT 
        g.urn,
        COUNT(u.entity_urn) as usage_count
    FROM glossary_export g
    LEFT JOIN glossary_term_usage u ON g.urn = u.glossary_term_urn
    WHERE g.entity_type = 'glossary_term'
    GROUP BY g.urn
)
GROUP BY adoption_level
ORDER BY adoption_level;
```

## Understanding the Data

### Table: glossary_term_usage

| Column | What It Means | Example |
|--------|---------------|---------|
| glossary_term_name | The business term | "Revenue" |
| entity_name | What's using the term | "Sales Dashboard" |
| entity_type | Type of asset | dashboard, dataset, chart |
| entity_subtype | More specific type | Report, Table, View |
| platform | Where it lives | powerbi, tableau, snowflake |
| container_name | Parent container | "Sales Workspace", "analytics_schema" |
| domain_name | Business domain | "Sales Domain" |

## Troubleshooting

### No Data in Usage Table?

**Check if entities are tagged:**
1. Go to DataHub UI
2. Find a Power BI report or dashboard
3. Check if it has glossary terms applied
4. If not, add tags and re-run the action

**Check permissions:**
- Ensure your DataHub token has read access to all entity types
- Test with: `SELECT COUNT(*) FROM glossary_export WHERE entity_type = 'glossary_term'`

### Action Taking Too Long?

**For large glossaries (100+ terms):**
- This is normal - it processes one term at a time
- Check logs to see progress
- Consider running during off-hours

**Expected runtimes:**
- 10 terms: ~30 seconds
- 50 terms: ~2-3 minutes  
- 100+ terms: ~5-10 minutes

### Only Seeing Some Platforms?

**This is normal!** You only see platforms that:
1. Are ingested into DataHub
2. Have entities with glossary terms applied
3. Are supported (Dashboard, Chart, Dataset, DataJob types)

## Next Steps

### 1. Explore More Queries

See [example_usage_queries.sql](../example_usage_queries.sql) for 20+ production-ready queries covering:
- Domain analysis
- Cross-platform usage
- Hierarchical analysis
- Time-based adoption
- Quality checks

### 2. Read the Full Guide

See [Glossary Usage Guide](GLOSSARY_USAGE_GUIDE.md) for:
- Detailed use cases
- Performance tuning
- Advanced queries
- Best practices

### 3. Set Up Alerts

Create alerts for:
- New unused terms (weekly)
- Cross-domain term usage (daily)
- Reports without domains (weekly)

### 4. Create Dashboards

Build executive dashboards showing:
- Term adoption trends
- Platform coverage
- Governance metrics
- Impact analysis

## Quick Reference

### Most Common Queries

```sql
-- Power BI reports using a term
SELECT entity_name FROM glossary_term_usage 
WHERE glossary_term_name = 'YourTerm' AND platform = 'powerbi';

-- Impact analysis
SELECT entity_type, COUNT(*) FROM glossary_term_usage 
WHERE glossary_term_name = 'YourTerm' GROUP BY entity_type;

-- Top used terms
SELECT glossary_term_name, COUNT(*) as count FROM glossary_term_usage 
GROUP BY glossary_term_name ORDER BY count DESC LIMIT 10;

-- Unused terms
SELECT name FROM glossary_export WHERE entity_type = 'glossary_term' 
AND urn NOT IN (SELECT glossary_term_urn FROM glossary_term_usage);

-- Platform summary
SELECT platform, COUNT(DISTINCT glossary_term_urn) as terms 
FROM glossary_term_usage GROUP BY platform;
```

## Get Help

- **Documentation**: See [Glossary Usage Guide](GLOSSARY_USAGE_GUIDE.md)
- **Examples**: See [example_usage_queries.sql](../example_usage_queries.sql)
- **Main README**: See [README](../README.md)
- **Issues**: Open a GitHub issue
- **Testing**: Run `python test_usage_functionality.py`

---

**You're ready to go!** Start with the common queries above and explore from there. 🚀

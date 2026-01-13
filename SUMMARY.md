# DataHub Glossary Export Action - Summary

**Author**: Brock Griffey  
**Date**: January 13, 2026  
**Version**: 0.1.0

## Overview

This is a complete DataHub Action that exports your entire glossary structure (terms, nodes, hierarchy, domains, and ownership) to a Snowflake table for analysis, reporting, and integration with other tools.

## What's Included

### Core Files

1. **`action_glossary_export/glossary_export_action.py`** - Main action implementation
   - Exports glossary terms and nodes using GraphQL
   - Creates/updates Snowflake table
   - Handles hierarchical relationships
   - Processes domains and ownership

2. **`action_glossary_export/__init__.py`** - Package initialization

3. **`setup.py`** - Package installation configuration
   - Dependencies: `acryl-datahub-actions`, `snowflake-connector-python`, `pydantic`
   - Entry point registration for DataHub Actions framework

### Configuration & Documentation

4. **`example_action.yaml`** - Sample configuration file
   - Shows how to configure Snowflake connection
   - Demonstrates environment variable usage
   - Includes all available settings

5. **`README.md`** - Complete documentation
   - Installation instructions (local and DataHub Cloud)
   - Configuration guide
   - Output table schema
   - Example queries
   - Troubleshooting tips

6. **`DEPLOYMENT.md`** - DataHub Cloud deployment guide
   - Step-by-step deployment instructions
   - Secret management
   - Monitoring and verification
   - Advanced configurations

7. **`example_queries.sql`** - 30+ SQL queries for common use cases
   - Basic queries (view terms, nodes, counts)
   - Hierarchy analysis
   - Domain analysis
   - Ownership reporting
   - Custom properties
   - Search and discovery
   - Data quality checks
   - Executive reporting

### Supporting Files

8. **`.gitignore`** - Excludes build artifacts, credentials, etc.
9. **`.gitattributes`** - Ensures consistent line endings
10. **`LICENSE`** - Apache 2.0 license

## Key Features

✅ **Complete Glossary Export**
- All glossary terms with properties
- All glossary nodes (hierarchy folders)
- Parent-child relationships
- Hierarchical paths

✅ **Rich Metadata**
- Term descriptions and definitions
- Creation timestamps
- Custom properties (as JSON)
- Ownership information (as JSON)

✅ **Domain Integration**
- Domain URN and name for each term
- Easy filtering by domain
- Cross-domain analysis

✅ **Snowflake Integration**
- Automatic table creation
- VARIANT columns for flexible JSON storage
- Full table refresh (truncate + insert)
- Timestamp tracking

✅ **Enterprise Ready**
- Configurable batch sizes for large glossaries
- Error handling and logging
- Environment variable support for secrets
- DataHub Cloud compatible

## Data Model

The action creates a Snowflake table with this schema:

```sql
CREATE TABLE glossary_export (
    urn VARCHAR(500) PRIMARY KEY,           -- Unique identifier
    name VARCHAR(500),                      -- Display name
    entity_type VARCHAR(50),                -- 'glossary_term' or 'glossary_node'
    description VARCHAR(16777216),          -- Full description
    parent_node_urn VARCHAR(500),           -- Parent folder URN
    parent_node_name VARCHAR(500),          -- Parent folder name
    hierarchical_path VARCHAR(16777216),    -- Full path (e.g., "Finance > Accounting > Revenue")
    domain_urn VARCHAR(500),                -- Associated domain URN
    domain_name VARCHAR(500),               -- Associated domain name
    custom_properties VARIANT,              -- JSON object of custom metadata
    ownership VARIANT,                      -- JSON array of owners
    created_at TIMESTAMP_NTZ,               -- Creation time
    last_updated TIMESTAMP_NTZ              -- Last export time
)
```

## How It Works

1. **Initialization**: When the action starts, it:
   - Connects to Snowflake
   - Creates the target table if it doesn't exist
   - Connects to DataHub's GraphQL API

2. **Data Fetching**: The action:
   - Queries all glossary terms using GraphQL search
   - Queries all glossary nodes using GraphQL search
   - Batches queries for performance (configurable batch size)

3. **Data Transformation**: For each entity:
   - Extracts core properties (name, description, etc.)
   - Builds hierarchical paths from parent relationships
   - Flattens domain information
   - Serializes custom properties to JSON
   - Serializes ownership to JSON

4. **Data Loading**: The action:
   - Truncates the existing table (full refresh)
   - Inserts all transformed rows
   - Updates the `last_updated` timestamp

## Usage Patterns

### Pattern 1: One-Time Export
Run the action once to export current glossary state for analysis:
```bash
datahub actions -c action.yaml
```

### Pattern 2: Scheduled Export
Schedule the action in DataHub Cloud to run daily/weekly for:
- Regular backups
- Change tracking over time
- Reporting dashboards

### Pattern 3: Event-Driven (Future Enhancement)
Could be modified to listen for glossary change events and update incrementally.

## Common Use Cases

### 1. Business Glossary Reports
Export glossary to Snowflake → Create Tableau/PowerBI dashboards → Share with stakeholders

### 2. Glossary Coverage Analysis
- Which domains have the most terms?
- Which terms lack descriptions?
- Which terms need owners?

### 3. Data Governance
- Track glossary completeness over time
- Identify gaps in business definitions
- Monitor adoption by domain

### 4. Integration with Other Systems
- Export glossary to feed other tools
- Sync definitions to documentation systems
- Provide glossary API via Snowflake views

### 5. Search and Discovery
- Full-text search across all terms
- Find related terms by domain
- Browse hierarchy programmatically

## Example Queries

```sql
-- Get all terms in Finance domain
SELECT name, description, hierarchical_path
FROM glossary_export
WHERE domain_name = 'Finance'
  AND entity_type = 'glossary_term';

-- Find terms without owners
SELECT name, hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
  AND (ownership IS NULL OR ARRAY_SIZE(ownership) = 0);

-- Glossary completeness scorecard
SELECT 
    COUNT(*) as total_terms,
    COUNT(CASE WHEN description IS NOT NULL THEN 1 END) as with_description,
    COUNT(CASE WHEN domain_name IS NOT NULL THEN 1 END) as with_domain,
    COUNT(CASE WHEN ownership IS NOT NULL THEN 1 END) as with_owner
FROM glossary_export
WHERE entity_type = 'glossary_term';
```

## Deployment Options

### Option 1: Local Execution
- Install locally with `pip install -e .`
- Run with `datahub actions -c action.yaml`
- Best for development and testing

### Option 2: DataHub Cloud
- Deploy as a custom action using Remote Action Source
- Configure via ingestion source UI
- Add as Extra Pip Library from GitHub
- Best for production use

### Option 3: Kubernetes/Docker
- Build Docker image with action installed
- Deploy as a cron job
- Best for enterprise infrastructure

## Configuration Example (DataHub Cloud)

```yaml
source:
  type: datahub_integrations.sources.remote_actions.remote_action_source.RemoteActionSource
  config:
    action_spec:
      type: action-glossary-export
      config:
        snowflake:
          account: "xy12345.us-east-1"
          user: "datahub_svc"
          password: "${SNOWFLAKE_PASSWORD}"
          warehouse: "COMPUTE_WH"
          database: "ANALYTICS"
          schema: "DATAHUB"
          table_name: "glossary_export"
        export_on_startup: true
        batch_size: 1000
    stage: live
    action_urn: 'urn:li:dataHubAction:glossary-export-v1'
```

Extra Pip Libraries:
```json
["/datahub-integrations-service","https://github.com/your-org/datahub-action-glossary-export/archive/main.zip"]
```

## Customization Ideas

### Extend the Data Model
- Add more metadata fields
- Include term relationships (IsA, HasA)
- Add term-to-asset associations

### Incremental Updates
- Listen to EntityChangeEvent
- Use MERGE instead of truncate/insert
- Track change history

### Multi-Warehouse Support
- Add Databricks/BigQuery connectors
- Support multiple destination types
- Abstract the destination layer

### Advanced Reporting
- Calculate glossary metrics
- Track trends over time
- Generate automated insights

## Testing

To test the action:

1. **Local Testing**:
   ```bash
   export DATAHUB_TOKEN="your-token"
   export SNOWFLAKE_PASSWORD="your-password"
   datahub actions -c example_action.yaml
   ```

2. **Verify in Snowflake**:
   ```sql
   SELECT COUNT(*) FROM glossary_export;
   SELECT entity_type, COUNT(*) FROM glossary_export GROUP BY entity_type;
   ```

3. **Check Logs**:
   - Look for "Glossary export completed successfully!"
   - Verify row counts match expectations

## Performance Considerations

- **Batch Size**: Default 1000, adjust based on glossary size
- **Network**: GraphQL queries are batched to minimize round-trips
- **Snowflake**: Full refresh is fast for small-medium glossaries (<10K terms)
- **Memory**: Processes data in batches, memory-efficient

## Security Best Practices

1. **Never commit credentials** - Use environment variables or secrets
2. **Use service accounts** - Don't use personal Snowflake accounts
3. **Limit permissions** - Grant only necessary Snowflake permissions
4. **Rotate tokens** - Regularly rotate DataHub and Snowflake credentials
5. **Use secrets management** - Leverage DataHub Cloud secrets or HashiCorp Vault

## Next Steps

1. **Publish to GitHub** - Push the action to your repository
2. **Test Locally** - Verify it works with your DataHub instance
3. **Deploy to DataHub Cloud** - Follow DEPLOYMENT.md instructions
4. **Create Dashboards** - Use example_queries.sql to build reports
5. **Schedule Regular Runs** - Set up daily/weekly exports
6. **Monitor and Maintain** - Check logs, verify data quality

## Support and Contributing

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: See README.md and DEPLOYMENT.md
- **Examples**: See example_action.yaml and example_queries.sql
- **Community**: Join DataHub Slack for questions

## License

Apache License 2.0 - See LICENSE file for details.

---

**Ready to Deploy?** Start with the [DEPLOYMENT.md](DEPLOYMENT.md) guide!

# DataHub Action: Glossary Export to Snowflake

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)
[![DataHub](https://img.shields.io/badge/DataHub-Compatible-blue)](https://datahubproject.io/)
[![Snowflake](https://img.shields.io/badge/Snowflake-Compatible-blue)](https://www.snowflake.com/)

**Author**: Jonny Dixon  
**Date**: January 13, 2026

## Overview

This DataHub Action exports your entire glossary structure to a Snowflake table, including:

- **Glossary Terms**: All business glossary terms with their properties
- **Glossary Nodes**: Hierarchical folder structure organizing terms
- **Domain Associations**: Links between glossary terms and domains
- **Ownership Information**: Technical and business owners
- **Custom Properties**: Any custom metadata attached to terms or nodes

## Features

- ✅ Complete glossary export (terms + nodes + hierarchy)
- ✅ Domain associations
- ✅ Ownership tracking
- ✅ Custom properties support
- ✅ Automatic table creation
- ✅ Full table refresh (truncate and reload)
- ✅ Configurable batch size for large glossaries
- ✅ Can run in DataHub Cloud or standalone

## Installation

### Local Installation

```bash
python -m pip install -e .
```

### DataHub Cloud Installation

When deploying to DataHub Cloud, add the following to the "Extra Pip Libraries" field in Step 5 of the ingestion source setup:

```json
["/datahub-integrations-service", "https://github.com/your-org/datahub-action-glossary-export/releases/download/v0.1.3/datahub_action_glossary_export-0.1.3-py3-none-any.whl"]
```

Replace:
- `your-org` with your GitHub organization name
- `v0.1.3` with the specific release version you want to deploy

**Note**: Use the wheel file (`.whl`) from GitHub releases, not the archive (`.zip`). The `/datahub-integrations-service` path provides the required `datahub_integrations` module.

## Configuration

Create an `action.yaml` file with the following structure:

```yaml
name: glossary-export-to-snowflake

source:
  type: "datahub-cloud"
  config:
    kill_after_idle_timeout: false

action:
  type: "action-glossary-export"
  config:
    # Snowflake connection (uses DataHub's SnowflakeConnectionConfig)
    connection:
      account_id: "xy12345"
      username: "your-username"
      password: "${SNOWFLAKE_PASSWORD}"
      warehouse: "COMPUTE_WH"
      role: "ACCOUNTADMIN"
      authentication_type: "DEFAULT_AUTHENTICATOR"
    
    # Destination
    destination:
      database: "DATAHUB"
      schema: "METADATA"
      table_name: "glossary_export"
    
    export_on_startup: true
    batch_size: 1000

datahub:
  server: "http://localhost:8080"
  token: "${DATAHUB_TOKEN}"
```

### Configuration Parameters

#### Snowflake Connection Configuration

**This action uses DataHub's `SnowflakeConnectionConfig`**, which means it supports all the same authentication methods as the DataHub Snowflake connector!

**Basic (Password) Authentication:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `account_id` | Yes | Snowflake account identifier (e.g., `xy12345`, `xy12345.us-east-2.aws`) |
| `username` | Yes | Snowflake username |
| `password` | Yes | Snowflake password (use environment variable) |
| `warehouse` | No | Snowflake warehouse name |
| `role` | No | Snowflake role |
| `authentication_type` | No | Authentication method (default: `DEFAULT_AUTHENTICATOR`) |

**Key Pair Authentication:**

```yaml
connection:
  account_id: "xy12345"
  username: "your-username"
  warehouse: "COMPUTE_WH"
  role: "ACCOUNTADMIN"
  authentication_type: "KEY_PAIR_AUTHENTICATOR"
  private_key_path: "/path/to/private_key.pem"
  private_key_password: "${PRIVATE_KEY_PASSWORD}"  # If encrypted
```

**OAuth Authentication:**

```yaml
connection:
  account_id: "xy12345"
  username: "your-username"
  warehouse: "COMPUTE_WH"
  authentication_type: "OAUTH_AUTHENTICATOR"
  oauth_config:
    provider: "microsoft"
    client_id: "${OAUTH_CLIENT_ID}"
    client_secret: "${OAUTH_CLIENT_SECRET}"
    authority_url: "https://login.microsoftonline.com/${TENANT_ID}"
    scopes:
      - "https://analysis.windows.net/powerbi/api/.default"
```

See [DataHub Snowflake connector docs](https://datahubproject.io/docs/generated/ingestion/sources/snowflake/) for complete authentication options.

#### Destination Configuration

| Parameter | Required | Description |
|-----------|----------|-------------|
| `database` | Yes | Target database name |
| `schema` | Yes | Target schema name |
| `table_name` | No | Target table name (default: `datahub_glossary_export`) |

#### Action Configuration

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `export_on_startup` | No | `true` | Export glossary immediately when action starts |
| `batch_size` | No | `1000` | Number of entities to fetch per GraphQL query |

## Output Table Schema

The action creates a Snowflake table with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `urn` | VARCHAR(500) | Primary key, entity URN |
| `name` | VARCHAR(500) | Entity name |
| `entity_type` | VARCHAR(50) | Either `glossary_term` or `glossary_node` |
| `description` | VARCHAR(16777216) | Entity description |
| `parent_node_urn` | VARCHAR(500) | Parent node URN (if any) |
| `parent_node_name` | VARCHAR(500) | Parent node name |
| `hierarchical_path` | VARCHAR(16777216) | Full hierarchical path (e.g., "Finance > Accounting > Revenue") |
| `domain_urn` | VARCHAR(500) | Associated domain URN |
| `domain_name` | VARCHAR(500) | Associated domain name |
| `custom_properties` | VARIANT | JSON object of custom properties |
| `ownership` | VARIANT | JSON array of owners with type information |
| `created_at` | TIMESTAMP_NTZ | Creation timestamp |
| `last_updated` | TIMESTAMP_NTZ | Last update timestamp (auto-updated) |

## Running the Action

### Local Execution

Set up environment variables:

```bash
export DATAHUB_TOKEN="<your-datahub-token>"
export SNOWFLAKE_PASSWORD="<your-snowflake-password>"
```

Run the action:

```bash
datahub actions -c action.yaml
```

### DataHub Cloud Execution

1. Navigate to **Ingestion** > **Sources** in DataHub Cloud
2. Click **Create new source**
3. Select **Custom Source** or use the Remote Action Source
4. Configure the source with this recipe:

```yaml
source:
  type: datahub_integrations.sources.remote_actions.remote_action_source.RemoteActionSource
  config:
    action_spec:
      type: action-glossary-export
      config:
        # Snowflake connection configuration
        connection:
          account_id: "xy12345"  # Snowflake account identifier
          username: "your-username"
          password: "${SNOWFLAKE_PASSWORD}"
          warehouse: "COMPUTE_WH"
          role: "ACCOUNTADMIN"
          authentication_type: "DEFAULT_AUTHENTICATOR"
        
        # Destination configuration  
        destination:
          database: "DATAHUB"
          schema: "METADATA"
          table_name: "glossary_export"
        
        # Export settings
        export_on_startup: true
        batch_size: 1000
    stage: live
    action_urn: 'urn:li:dataHubAction:glossary-export'
```

5. In **Step 5 (Advanced)**, add the Extra Pip Libraries
6. Set secrets for `SNOWFLAKE_PASSWORD` and `DATAHUB_TOKEN`
7. Save and run the ingestion source

## Querying the Data

Once exported, you can query the glossary data in Snowflake:

```sql
-- Get all glossary terms with their domains
SELECT 
    name,
    description,
    hierarchical_path,
    domain_name
FROM glossary_export
WHERE entity_type = 'glossary_term'
ORDER BY hierarchical_path;

-- Get glossary hierarchy
SELECT 
    name,
    entity_type,
    parent_node_name,
    hierarchical_path
FROM glossary_export
ORDER BY hierarchical_path;

-- Get terms by domain
SELECT 
    domain_name,
    COUNT(*) as term_count
FROM glossary_export
WHERE entity_type = 'glossary_term'
    AND domain_name IS NOT NULL
GROUP BY domain_name;

-- Get ownership information
SELECT 
    name,
    ownership:type as owner_type,
    ownership:username as owner_username
FROM glossary_export,
LATERAL FLATTEN(input => ownership)
WHERE entity_type = 'glossary_term';
```

## Troubleshooting

### Action Not Starting

- Verify Extra Pip Libraries are correctly formatted
- Check that your repository is publicly accessible
- Review ingestion source logs for pip installation errors

### Connection Errors

- Verify Snowflake credentials are correct
- Ensure the Snowflake role has permissions to create tables and insert data
- Check network connectivity to Snowflake

### No Data Exported

- Verify the DataHub token has read access to glossary entities
- Check that glossary terms/nodes exist in DataHub
- Review action logs for GraphQL query errors

### Action Stops After 30 Seconds

If using the DataHub event source, set `kill_after_idle_timeout: false` in the source config:

```yaml
source:
  type: "datahub-cloud"
  config:
    kill_after_idle_timeout: false
```

## Development

To contribute or customize this action:

```bash
# Clone the repository
git clone https://github.com/your-org/datahub-action-glossary-export.git
cd datahub-action-glossary-export

# Install in development mode
pip install -e .

# Make your changes to action_glossary_export/glossary_export_action.py

# Test locally
datahub actions -c example_action.yaml
```

## License

Copyright 2026 Acryl Data, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

## Support

For issues or questions, please:
- Open an issue on GitHub
- Contact the DataHub team
- Check the [DataHub Actions documentation](https://datahubproject.io/docs/actions)

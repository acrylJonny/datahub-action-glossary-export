# Deployment Guide for DataHub Cloud

**Author**: Jonny Dixon  
**Date**: January 13, 2026

This guide provides step-by-step instructions for deploying the Glossary Export action to DataHub Cloud.

## Prerequisites

1. Access to DataHub Cloud with permissions to create ingestion sources
2. A Snowflake account with:
   - Write permissions to a database and schema
   - A warehouse to use for queries
3. The action code published to a Git repository (GitHub recommended)

## Step 1: Publish Your Action to GitHub

Push this action to a GitHub repository:

```bash
cd datahub-action-glossary-export
git init
git add .
git commit -m "Initial commit: Glossary Export action"
git remote add origin https://github.com/your-org/datahub-action-glossary-export.git
git push -u origin main
```

Make sure the repository is either:
- Public, or
- Private with proper access credentials configured in DataHub Cloud

## Step 2: Set Up Secrets in DataHub Cloud

Before creating the ingestion source, set up the following secrets in DataHub Cloud:

1. Navigate to **Settings** > **Secrets**
2. Create the following secrets:
   - `SNOWFLAKE_PASSWORD`: Your Snowflake password
   - `DATAHUB_TOKEN`: Your DataHub API token (if not using default)

## Step 3: Create a New Ingestion Source

1. **Navigate to Ingestion Sources**
   - Go to **Ingestion** > **Sources**
   - Click **Create new source**

2. **Configure the Source (Step 1-4)**
   - Source name: `glossary-export-to-snowflake`
   - Recipe:

```yaml
source:
  type: datahub_integrations.sources.remote_actions.remote_action_source.RemoteActionSource
  config:
    action_spec:
      type: action-glossary-export
      config:
        # Snowflake connection configuration
        connection:
          account_id: "xy12345"  # Snowflake account identifier (without .snowflakecomputing.com)
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
    action_urn: 'urn:li:dataHubAction:glossary-export-v1'
```

3. **Configure Extra Pip Libraries (Step 5 - Advanced)**
   - Click **Advanced**
   - In the **Extra Pip Libraries** field, add:

```json
["/datahub-integrations-service", "https://github.com/your-org/datahub-action-glossary-export/releases/download/v0.1.3/datahub_action_glossary_export-0.1.3-py3-none-any.whl"]
```

   Replace:
   - `your-org` with your GitHub organization/username
   - `v0.1.3` with the specific release version you want to deploy
   
   **Important**: Use the wheel file (`.whl`) from GitHub releases, not the archive (`.zip`). The `/datahub-integrations-service` path is a special reference that DataHub Cloud recognizes to install the integrations service package required for `RemoteActionSource`.

4. **Schedule (Optional)**
   - You can schedule this to run periodically if you want regular exports
   - For one-time exports, just run it manually

5. **Review and Create**
   - Review your configuration
   - Click **Save and Run**

## Step 4: Monitor Execution

1. After creating the source, it will start executing immediately
2. Click on the source to view execution logs
3. Look for log messages like:
   - "Connecting to Snowflake..."
   - "Fetching all glossary terms..."
   - "Total glossary terms fetched: X"
   - "Successfully inserted X rows into Snowflake"
   - "Glossary export completed successfully!"

## Step 5: Verify Data in Snowflake

Connect to Snowflake and run:

```sql
-- Check if table exists
SHOW TABLES LIKE 'glossary_export';

-- Check row count
SELECT COUNT(*) FROM glossary_export;

-- View sample data
SELECT * FROM glossary_export LIMIT 10;

-- Check data by type
SELECT entity_type, COUNT(*) 
FROM glossary_export 
GROUP BY entity_type;
```

## Troubleshooting

### Installation Issues

**Error: "Failed to install package"**
- Check that the GitHub URL is correct and accessible
- Verify the repository is public or credentials are configured
- Try using a specific commit hash instead of `main`:
  ```
  https://github.com/your-org/datahub-action-glossary-export/archive/abc1234.zip
  ```

### Connection Issues

**Error: "Failed to connect to Snowflake"**
- Verify Snowflake credentials are correct
- Check that the secret `SNOWFLAKE_PASSWORD` is properly set
- Ensure the Snowflake account identifier is in the correct format
- Verify network connectivity (check if DataHub Cloud IP needs whitelisting)

**Error: "Permission denied"**
- Ensure the Snowflake user has permissions to:
  - Create tables in the target schema
  - Insert data into tables
  - Use the specified warehouse

### Data Issues

**Error: "No data exported"**
- Verify the DataHub token has read access to glossary entities
- Check that glossary terms/nodes exist in DataHub
- Review action logs for GraphQL query errors

### Action Stops After 30 Seconds

This is a known issue with the default event source configuration. The action runs on startup and completes its export, but the pipeline may exit after 30 seconds of idle time. This is expected behavior for a one-time export action.

If you need the action to stay alive:
- Use a different source type (not datahub-cloud events)
- Or schedule it to run periodically

## Running on a Schedule

To export the glossary on a regular schedule:

1. Set up a scheduled execution in DataHub Cloud
2. Configure the schedule (e.g., daily at 2 AM)
3. The action will export the glossary each time it runs

Example schedule configuration:
- **Frequency**: Daily
- **Time**: 02:00 UTC
- **Timezone**: UTC

## Manual Execution

You can also trigger the export manually:

1. Go to **Ingestion** > **Sources**
2. Find your `glossary-export-to-snowflake` source
3. Click **Execute**
4. Monitor the logs for completion

## Advanced Configuration

### Using Private GitHub Repository

If your action is in a private repository:

1. Generate a GitHub Personal Access Token with `repo` scope
2. Create a secret in DataHub Cloud: `GITHUB_TOKEN`
3. Modify the Extra Pip Libraries field:

```json
["/datahub-integrations-service","https://${GITHUB_TOKEN}@github.com/your-org/datahub-action-glossary-export/archive/main.zip"]
```

### Custom Table Schema

If you need to customize the Snowflake table schema, modify the `_create_table_if_not_exists` method in `glossary_export_action.py` before publishing.

### Incremental Updates

The current implementation does a full refresh (truncate and reload). For incremental updates, you would need to:

1. Modify the action to track changes
2. Use MERGE statements instead of INSERT
3. Listen to specific DataHub events (term creation, updates, deletions)

## Support

For issues or questions:
- Check the [DataHub Actions documentation](https://datahubproject.io/docs/actions)
- Check the [CHANGELOG.md](./CHANGELOG.md) for version history
- Open an issue on GitHub
- Contact your DataHub Cloud support team

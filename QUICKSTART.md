# Quick Start Guide

Get the Glossary Export action running in 5 minutes!

## Prerequisites

- DataHub instance (Cloud or self-hosted)
- Snowflake account with write permissions
- Python 3.8+ (for local testing)

## Option A: Local Testing (Fastest)

### 1. Clone and Install

```bash
cd datahub-action-glossary-export
pip install -e .
```

### 2. Configure

Edit `example_action.yaml` with your credentials:

```yaml
action:
  config:
    snowflake:
      account: "your-account.snowflakecomputing.com"
      user: "your-username"
      password: "${SNOWFLAKE_PASSWORD}"
      warehouse: "COMPUTE_WH"
      database: "DATAHUB"
      schema: "METADATA"
      table_name: "glossary_export"

datahub:
  server: "http://localhost:8080"  # or your DataHub URL
  token: "${DATAHUB_TOKEN}"
```

### 3. Set Environment Variables

```bash
export DATAHUB_TOKEN="your-datahub-token"
export SNOWFLAKE_PASSWORD="your-snowflake-password"
```

### 4. Run

```bash
datahub actions -c example_action.yaml
```

### 5. Verify

```sql
-- In Snowflake
SELECT COUNT(*) FROM DATAHUB.METADATA.glossary_export;
SELECT * FROM DATAHUB.METADATA.glossary_export LIMIT 10;
```

## Option B: DataHub Cloud (Production)

### 1. Publish to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-org/datahub-action-glossary-export.git
git push -u origin main
```

### 2. Create Secrets in DataHub Cloud

- Go to **Settings** > **Secrets**
- Add `SNOWFLAKE_PASSWORD`

### 3. Create Ingestion Source

**Recipe**:
```yaml
source:
  type: datahub_integrations.sources.remote_actions.remote_action_source.RemoteActionSource
  config:
    action_spec:
      type: action-glossary-export
      config:
        snowflake:
          account: "your-account.snowflakecomputing.com"
          user: "your-username"
          password: "${SNOWFLAKE_PASSWORD}"
          warehouse: "COMPUTE_WH"
          database: "DATAHUB"
          schema: "METADATA"
          table_name: "glossary_export"
    stage: live
    action_urn: 'urn:li:dataHubAction:glossary-export'
```

**Extra Pip Libraries** (Step 5 - Advanced):
```json
["/datahub-integrations-service","https://github.com/your-org/datahub-action-glossary-export/archive/main.zip"]
```

### 4. Run and Monitor

- Click **Save and Run**
- Monitor logs for "Glossary export completed successfully!"

### 5. Verify in Snowflake

```sql
SELECT COUNT(*) FROM glossary_export;
SELECT entity_type, COUNT(*) FROM glossary_export GROUP BY entity_type;
```

## What You Get

After running, you'll have a Snowflake table with:
- ✅ All glossary terms
- ✅ All glossary nodes (folders)
- ✅ Hierarchical paths
- ✅ Domain associations
- ✅ Ownership information
- ✅ Custom properties

## Quick Queries

```sql
-- View all terms
SELECT name, description, hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term';

-- Terms by domain
SELECT domain_name, COUNT(*) as count
FROM glossary_export
WHERE entity_type = 'glossary_term'
GROUP BY domain_name;

-- Terms without owners
SELECT name, hierarchical_path
FROM glossary_export
WHERE entity_type = 'glossary_term'
  AND (ownership IS NULL OR ARRAY_SIZE(ownership) = 0);
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🚀 See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- 📊 Use [example_queries.sql](example_queries.sql) for reporting
- 📋 Check [SUMMARY.md](SUMMARY.md) for complete overview

## Troubleshooting

### "Failed to connect to Snowflake"
→ Check account identifier format: `account.region.cloud` (e.g., `xy12345.us-east-1.aws`)

### "No data exported"
→ Verify DataHub token has read access to glossary entities

### "Permission denied in Snowflake"
→ Ensure user has CREATE TABLE and INSERT permissions on the schema

### "Action not found"
→ Check Extra Pip Libraries URL is correct and repository is accessible

## Get Help

- 💬 [DataHub Slack](https://datahubspace.slack.com)
- 📖 [DataHub Actions Docs](https://datahubproject.io/docs/actions)
- 🐛 [GitHub Issues](https://github.com/your-org/datahub-action-glossary-export/issues)

---

**Happy Exporting!** 🚀

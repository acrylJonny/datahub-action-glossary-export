# Snowflake Connection Setup Guide

This action uses **DataHub's `SnowflakeConnectionConfig`**, which means it supports all the same enterprise-grade authentication methods as the DataHub Snowflake connector!

## Authentication Methods

### 1. Password Authentication (Default)

The simplest method using username and password:

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  password: "${SNOWFLAKE_PASSWORD}"
  warehouse: "COMPUTE_WH"
  role: "DATAHUB_ROLE"
  authentication_type: "DEFAULT_AUTHENTICATOR"  # Optional, this is the default
```

### 2. Key Pair Authentication (Recommended for Production)

More secure authentication using RSA key pairs:

**Step 1: Generate Key Pair**

```bash
# Generate private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# Generate public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

**Step 2: Add Public Key to Snowflake User**

```sql
ALTER USER datahub_user SET RSA_PUBLIC_KEY='MIIBIjANBgkqhki...';
```

**Step 3: Configure Action**

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  warehouse: "COMPUTE_WH"
  role: "DATAHUB_ROLE"
  authentication_type: "KEY_PAIR_AUTHENTICATOR"
  private_key_path: "/path/to/rsa_key.p8"
  # If your private key is encrypted:
  # private_key_password: "${PRIVATE_KEY_PASSWORD}"
```

**Or using inline private key:**

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  warehouse: "COMPUTE_WH"
  authentication_type: "KEY_PAIR_AUTHENTICATOR"
  private_key: |
    -----BEGIN PRIVATE KEY-----
    MIIEvgIBADANBgkqhkiG9w0BAQEFAAS...
    -----END PRIVATE KEY-----
```

### 3. OAuth Authentication

For organizations using OAuth identity providers:

#### Microsoft Azure AD

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  warehouse: "COMPUTE_WH"
  authentication_type: "OAUTH_AUTHENTICATOR"
  oauth_config:
    provider: "microsoft"
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    authority_url: "https://login.microsoftonline.com/${TENANT_ID}"
    scopes:
      - "https://analysis.windows.net/powerbi/api/.default"
```

#### Okta

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  warehouse: "COMPUTE_WH"
  authentication_type: "OAUTH_AUTHENTICATOR"
  oauth_config:
    provider: "okta"
    client_id: "${OKTA_CLIENT_ID}"
    client_secret: "${OKTA_CLIENT_SECRET}"
    authority_url: "https://your-domain.okta.com/oauth2/default"
    scopes:
      - "session:role:DATAHUB_ROLE"
```

### 4. External Browser Authentication

Opens a browser window for SSO authentication:

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  warehouse: "COMPUTE_WH"
  authentication_type: "EXTERNAL_BROWSER_AUTHENTICATOR"
```

**Note**: This method is not recommended for automated/scheduled runs as it requires manual browser interaction.

## Account Identifier Formats

Snowflake supports multiple account identifier formats:

### Format 1: Account Locator (Legacy)

```yaml
account_id: "xy12345"  # Just the account identifier
```

### Format 2: Account Locator with Region

```yaml
account_id: "xy12345.us-east-2.aws"  # AWS
account_id: "xy12345.us-central1.gcp"  # GCP
account_id: "xy12345.central-us.azure"  # Azure
```

### Format 3: Organization and Account Name

```yaml
account_id: "myorg-myaccount"  # Recommended for new accounts
```

**The action automatically handles all formats** - you don't need to include `.snowflakecomputing.com`.

## Advanced Connection Options

### Custom Snowflake Domain (China Region)

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  password: "${SNOWFLAKE_PASSWORD}"
  snowflake_domain: "snowflakecomputing.cn"  # For China region
```

### Connection Arguments

Pass additional arguments to the Snowflake connector:

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  password: "${SNOWFLAKE_PASSWORD}"
  connect_args:
    client_session_keep_alive: true
    client_prefetch_threads: 4
    socket_timeout: 300
```

### SQLAlchemy Options

```yaml
connection:
  account_id: "xy12345"
  username: "datahub_user"
  password: "${SNOWFLAKE_PASSWORD}"
  options:
    pool_size: 10
    max_overflow: 20
    pool_timeout: 30
```

## Complete Configuration Example

Here's a complete example with all settings:

```yaml
name: glossary-export-to-snowflake

source:
  type: "datahub-cloud"
  config:
    kill_after_idle_timeout: false

action:
  type: "action-glossary-export"
  config:
    # Connection configuration
    connection:
      # Basic settings
      account_id: "xy12345.us-east-2.aws"
      username: "datahub_service"
      warehouse: "DATAHUB_WH"
      role: "DATAHUB_ROLE"
      
      # Authentication (choose one method)
      # Option 1: Password
      password: "${SNOWFLAKE_PASSWORD}"
      authentication_type: "DEFAULT_AUTHENTICATOR"
      
      # Option 2: Key Pair (uncomment to use)
      # authentication_type: "KEY_PAIR_AUTHENTICATOR"
      # private_key_path: "/secrets/snowflake_private_key.p8"
      # private_key_password: "${PRIVATE_KEY_PASSWORD}"
      
      # Option 3: OAuth (uncomment to use)
      # authentication_type: "OAUTH_AUTHENTICATOR"
      # oauth_config:
      #   provider: "microsoft"
      #   client_id: "${OAUTH_CLIENT_ID}"
      #   client_secret: "${OAUTH_CLIENT_SECRET}"
      #   authority_url: "${OAUTH_AUTHORITY_URL}"
      
      # Advanced options (optional)
      connect_args:
        client_session_keep_alive: true
        client_prefetch_threads: 10
    
    # Destination configuration
    destination:
      database: "DATAHUB_METADATA"
      schema: "GLOSSARY"
      table_name: "glossary_export"
    
    # Export settings
    export_on_startup: true
    batch_size: 1000

datahub:
  server: "${DATAHUB_GMS_URL}"
  token: "${DATAHUB_TOKEN}"
```

## Required Snowflake Permissions

The Snowflake user needs these permissions:

```sql
-- Grant database and schema access
GRANT USAGE ON DATABASE DATAHUB_METADATA TO ROLE DATAHUB_ROLE;
GRANT USAGE ON SCHEMA DATAHUB_METADATA.GLOSSARY TO ROLE DATAHUB_ROLE;

-- Grant warehouse access
GRANT USAGE ON WAREHOUSE DATAHUB_WH TO ROLE DATAHUB_ROLE;

-- Grant table permissions
GRANT CREATE TABLE ON SCHEMA DATAHUB_METADATA.GLOSSARY TO ROLE DATAHUB_ROLE;
GRANT INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA DATAHUB_METADATA.GLOSSARY TO ROLE DATAHUB_ROLE;
GRANT INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA DATAHUB_METADATA.GLOSSARY TO ROLE DATAHUB_ROLE;

-- Assign role to user
GRANT ROLE DATAHUB_ROLE TO USER datahub_service;
```

## Testing Your Connection

You can test your Snowflake connection configuration before running the full export:

```bash
# Install the package
pip install -e .

# Test with a minimal Python script
python -c "
from datahub.ingestion.source.snowflake.snowflake_connection import SnowflakeConnectionConfig
config = SnowflakeConnectionConfig(
    account_id='xy12345',
    username='your-user',
    password='your-password',
    warehouse='COMPUTE_WH'
)
conn = config.get_native_connection()
print('✅ Connection successful!')
conn.close()
"
```

## Troubleshooting

### Error: "Account must be specified"

Make sure `account_id` is set and doesn't include `.snowflakecomputing.com`:

```yaml
# ❌ Wrong
account_id: "xy12345.snowflakecomputing.com"

# ✅ Correct
account_id: "xy12345"
```

### Error: "250001: Could not connect to Snowflake backend"

- Check that the account identifier is correct
- Verify network connectivity (firewall, VPN)
- Check if you need to allowlist DataHub Cloud IPs

### Error: "Incorrect username or password"

- Verify credentials are correct
- Check if the user is locked or expired in Snowflake
- For key pair auth, verify the public key is correctly set on the user

### Error: "Role 'XXXX' specified in the connect string does not exist"

- Verify the role exists: `SHOW ROLES;`
- Check that the user has been granted the role
- Try connecting without specifying a role (uses default role)

### Error: "002003: Database 'XXXX' does not exist or not authorized"

- Check the database name is correct (case-sensitive)
- Verify the role has USAGE permission on the database
- If using a share, verify it's configured correctly

## Best Practices

1. **Use Key Pair Authentication in Production** - More secure than passwords and supports rotation
2. **Use Service Accounts** - Don't use personal user accounts for automated processes
3. **Limit Role Permissions** - Grant only the minimum necessary permissions
4. **Rotate Credentials Regularly** - Especially passwords and OAuth tokens
5. **Use Secrets Management** - Store credentials in DataHub Secrets or a vault system
6. **Monitor Connection Usage** - Track queries and performance in Snowflake
7. **Set Appropriate Warehouse Size** - Start small and scale if needed
8. **Use Auto-suspend Warehouses** - To minimize costs when not in use

## Reference

- [DataHub Snowflake Connector Docs](https://datahubproject.io/docs/generated/ingestion/sources/snowflake/)
- [Snowflake Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html)
- [Snowflake Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth.html)
- [Snowflake OAuth](https://docs.snowflake.com/en/user-guide/oauth.html)

---

**Questions?** Check the main [README.md](README.md) or [DEPLOYMENT.md](DEPLOYMENT.md) for more information.

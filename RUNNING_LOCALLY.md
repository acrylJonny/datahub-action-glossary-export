# Running Glossary Export Locally

Since DataHub Cloud's RemoteActionSource may have compatibility issues with custom packages, running the action locally is often more reliable and gives you more control.

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/acrylJonny/datahub-action-glossary-export.git
cd datahub-action-glossary-export

# Make the script executable
chmod +x run_local.sh

# Run the setup
./run_local.sh
```

This will create a `.env` template file on first run.

### 2. Configure Environment Variables

Edit the `.env` file with your credentials:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT_ID="xy12345"
SNOWFLAKE_USERNAME="jd_datahub_user"
SNOWFLAKE_PASSWORD="your-actual-password"
SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
SNOWFLAKE_ROLE="jd_datahub_role"
SNOWFLAKE_DATABASE="JONNY_DEMO"
SNOWFLAKE_SCHEMA="public"

# DataHub Configuration
DATAHUB_SERVER="https://your-instance.acryl.io"
DATAHUB_TOKEN="your-actual-token"
```

### 3. Run It

```bash
./run_local.sh
```

## Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package
pip install -e .

# Set environment variables
export SNOWFLAKE_ACCOUNT_ID="xy12345"
export SNOWFLAKE_USERNAME="jd_datahub_user"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export SNOWFLAKE_ROLE="jd_datahub_role"
export SNOWFLAKE_DATABASE="JONNY_DEMO"
export SNOWFLAKE_SCHEMA="public"
export DATAHUB_SERVER="https://your-instance.acryl.io"
export DATAHUB_TOKEN="your-token"

# Run the action
datahub actions -c glossary_export_local.yaml
```

## Scheduling with Cron

To run this daily (e.g., at 2 AM):

### 1. Create a cron-compatible script

```bash
cat > /path/to/run_glossary_export_cron.sh << 'EOF'
#!/bin/bash
cd /path/to/datahub-action-glossary-export
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
datahub actions -c glossary_export_local.yaml >> /var/log/glossary-export.log 2>&1
EOF

chmod +x /path/to/run_glossary_export_cron.sh
```

### 2. Add to crontab

```bash
crontab -e
```

Add this line:
```
0 2 * * * /path/to/run_glossary_export_cron.sh
```

### 3. Verify it's scheduled

```bash
crontab -l
```

## Scheduling with systemd (Linux)

For more robust scheduling on Linux systems:

### 1. Create service file

```bash
sudo cat > /etc/systemd/system/glossary-export.service << 'EOF'
[Unit]
Description=DataHub Glossary Export
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/datahub-action-glossary-export
EnvironmentFile=/path/to/datahub-action-glossary-export/.env
ExecStart=/path/to/datahub-action-glossary-export/venv/bin/datahub actions -c glossary_export_local.yaml
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### 2. Create timer file

```bash
sudo cat > /etc/systemd/system/glossary-export.timer << 'EOF'
[Unit]
Description=Run Glossary Export daily at 2 AM
Requires=glossary-export.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

### 3. Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable glossary-export.timer
sudo systemctl start glossary-export.timer

# Check status
sudo systemctl status glossary-export.timer
sudo systemctl list-timers --all
```

### 4. View logs

```bash
# Recent logs
sudo journalctl -u glossary-export.service -n 100

# Follow logs
sudo journalctl -u glossary-export.service -f
```

## Docker Deployment

For containerized deployment:

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install git (needed for pip install from GitHub)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /app/

# Install the package
RUN pip install --no-cache-dir -e .

# Run the action
CMD ["datahub", "actions", "-c", "glossary_export_local.yaml"]
```

### 2. Build and run

```bash
docker build -t glossary-export .

docker run -e SNOWFLAKE_ACCOUNT_ID="xy12345" \
           -e SNOWFLAKE_USERNAME="jd_datahub_user" \
           -e SNOWFLAKE_PASSWORD="your-password" \
           -e SNOWFLAKE_WAREHOUSE="COMPUTE_WH" \
           -e SNOWFLAKE_ROLE="jd_datahub_role" \
           -e SNOWFLAKE_DATABASE="JONNY_DEMO" \
           -e SNOWFLAKE_SCHEMA="public" \
           -e DATAHUB_SERVER="https://your-instance.acryl.io" \
           -e DATAHUB_TOKEN="your-token" \
           glossary-export
```

### 3. Schedule with Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: glossary-export
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: glossary-export
            image: glossary-export:latest
            envFrom:
            - secretRef:
                name: glossary-export-secrets
          restartPolicy: OnFailure
```

## Troubleshooting

### Check if action is installed correctly

```bash
source venv/bin/activate
pip show datahub-action-glossary-export
```

### Test Snowflake connection

```bash
python test_connection.py
```

### View DataHub Actions logs

```bash
# Increase verbosity
datahub actions -c glossary_export_local.yaml --debug
```

### Check Snowflake table

```sql
SELECT COUNT(*) FROM JONNY_DEMO.public.glossary_export;
SELECT * FROM JONNY_DEMO.public.glossary_export LIMIT 10;
```

## Advantages of Running Locally

1. **Full Control**: You manage the environment and dependencies
2. **Better Debugging**: Direct access to logs and error messages
3. **More Reliable**: No dependency on DataHub Cloud's execution environment
4. **Faster Iteration**: Test changes immediately without pushing to GitHub
5. **Custom Scheduling**: Use any scheduler (cron, systemd, Kubernetes, etc.)
6. **Security**: Credentials stored in your own environment

## Need Help?

- Check the main [README.md](README.md) for configuration details
- Review [SNOWFLAKE_SETUP.md](SNOWFLAKE_SETUP.md) for Snowflake permissions
- Open an issue on GitHub if you encounter problems

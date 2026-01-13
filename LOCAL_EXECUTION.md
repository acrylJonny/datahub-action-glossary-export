# Running Locally (Alternative to DataHub Cloud)

If you're experiencing issues with DataHub Cloud's RemoteActionSource, you can run this action locally or on your own infrastructure.

## Prerequisites

1. Python 3.9+ installed
2. Access to your DataHub instance
3. Snowflake credentials

## Setup

### 1. Install the action

```bash
cd datahub-action-glossary-export
pip install -e .
```

### 2. Configure environment variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# DataHub Connection
DATAHUB_SERVER=https://your-instance.acryl.io
DATAHUB_TOKEN=your-datahub-token-here

# Snowflake Connection
DATAHUB_SNOWFLAKE_ACCOUNT=xy12345
DATAHUB_SNOWFLAKE_PASSWORD=your-password-here
```

### 3. Run the export

```bash
./run_local.sh
```

Or manually:

```bash
export $(cat .env | grep -v '^#' | xargs)
datahub actions -c local_config.yaml
```

## Scheduling with Cron

To run this daily at 2 AM:

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths):
0 2 * * * cd /path/to/datahub-action-glossary-export && ./run_local.sh >> /var/log/glossary-export.log 2>&1
```

## Scheduling with SystemD (Linux)

Create `/etc/systemd/system/glossary-export.service`:

```ini
[Unit]
Description=DataHub Glossary Export
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/datahub-action-glossary-export
EnvironmentFile=/path/to/datahub-action-glossary-export/.env
ExecStart=/usr/local/bin/datahub actions -c local_config.yaml

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/glossary-export.timer`:

```ini
[Unit]
Description=Run Glossary Export Daily
Requires=glossary-export.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable glossary-export.timer
sudo systemctl start glossary-export.timer
```

## Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

CMD ["datahub", "actions", "-c", "local_config.yaml"]
```

Build and run:

```bash
docker build -t glossary-export .
docker run --env-file .env glossary-export
```

## Kubernetes CronJob

Create `k8s-cronjob.yaml`:

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
            image: your-registry/glossary-export:latest
            envFrom:
            - secretRef:
                name: glossary-export-secrets
          restartPolicy: OnFailure
```

Apply:

```bash
kubectl apply -f k8s-cronjob.yaml
```

## Troubleshooting

### Connection Issues

Test connectivity:

```bash
python test_connection.py
```

### Check Logs

```bash
# View recent execution
cat /var/log/glossary-export.log

# Follow live logs
tail -f /var/log/glossary-export.log
```

### Verify Installation

```bash
pip show datahub-action-glossary-export
datahub actions plugins
```

You should see `action-glossary-export` in the list of available actions.

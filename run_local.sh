#!/bin/bash
# Setup and run the glossary export action locally

set -e

echo "🚀 Setting up Glossary Export Action..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install the package
echo "📦 Installing glossary export action..."
pip install -e . -q

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << 'EOF'
# Snowflake Configuration
SNOWFLAKE_ACCOUNT_ID="xy12345"
SNOWFLAKE_USERNAME="jd_datahub_user"
SNOWFLAKE_PASSWORD="your-password-here"
SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
SNOWFLAKE_ROLE="jd_datahub_role"
SNOWFLAKE_DATABASE="JONNY_DEMO"
SNOWFLAKE_SCHEMA="public"

# DataHub Configuration
DATAHUB_SERVER="https://your-instance.acryl.io"
DATAHUB_TOKEN="your-token-here"
EOF
    echo "❌ Please edit .env file with your credentials and run again"
    exit 1
fi

# Load environment variables
echo "✓ Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Run the action
echo "🎯 Running glossary export..."
datahub actions -c glossary_export_local.yaml

echo "✅ Done!"

#!/bin/bash

# ========================================
# Deploy Salesforce Tools to Snowflake
# ========================================

set -e  # Exit on error

echo "========================================="
echo "Salesforce Tools - Snowflake Deployment"
echo "========================================="
echo ""

# Configuration
SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT:-}"
SNOWFLAKE_USER="${SNOWFLAKE_USER:-}"
SNOWFLAKE_DATABASE="${SNOWFLAKE_DATABASE:-TEST}"
SNOWFLAKE_SCHEMA="${SNOWFLAKE_SCHEMA:-PUBLIC}"
SNOWFLAKE_ROLE="${SNOWFLAKE_ROLE:-ACCOUNTADMIN}"
STAGE_NAME="SALESFORCE_STAGE"

# Check if Snow CLI is installed
if ! command -v snow &> /dev/null; then
    echo "❌ Snow CLI not found. Please install it first:"
    echo "   pip install snowflake-cli-labs"
    exit 1
fi

echo "✅ Snow CLI found"
echo ""

# Check if required files exist
echo "Checking required files..."
required_files=(
    "salesforce_tools/__init__.py"
    "salesforce_tools/core.py"
    "salesforce_tools/accounts.py"
    "salesforce_tools/opportunities.py"
    "salesforce_tools/contacts.py"
    "salesforce_tools/discovery.py"
    "snowflake_setup.sql"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file not found: $file"
        exit 1
    fi
    echo "  ✓ $file"
done

echo ""
echo "========================================="
echo "Step 1: Upload Python Files to Stage"
echo "========================================="
echo ""

# Upload Python files using Snow CLI
echo "Uploading salesforce_tools/__init__.py..."
snow stage copy \
    salesforce_tools/__init__.py \
    "@${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.${STAGE_NAME}/salesforce_tools/" \
    --overwrite \
    --auto-compress false

echo "Uploading salesforce_tools/core.py..."
snow stage copy \
    salesforce_tools/core.py \
    "@${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.${STAGE_NAME}/salesforce_tools/" \
    --overwrite \
    --auto-compress false

echo "Uploading salesforce_tools/accounts.py..."
snow stage copy \
    salesforce_tools/accounts.py \
    "@${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.${STAGE_NAME}/salesforce_tools/" \
    --overwrite \
    --auto-compress false

echo "Uploading salesforce_tools/opportunities.py..."
snow stage copy \
    salesforce_tools/opportunities.py \
    "@${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.${STAGE_NAME}/salesforce_tools/" \
    --overwrite \
    --auto-compress false

echo "Uploading salesforce_tools/contacts.py..."
snow stage copy \
    salesforce_tools/contacts.py \
    "@${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.${STAGE_NAME}/salesforce_tools/" \
    --overwrite \
    --auto-compress false

echo "Uploading salesforce_tools/discovery.py..."
snow stage copy \
    salesforce_tools/discovery.py \
    "@${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.${STAGE_NAME}/salesforce_tools/" \
    --overwrite \
    --auto-compress false

echo ""
echo "✅ Python files uploaded successfully"
echo ""

# Verify files are uploaded
echo "Verifying uploaded files..."
snow stage list "@${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.${STAGE_NAME}/salesforce_tools/"

echo ""
echo "========================================="
echo "Step 2: Execute Setup SQL Script"
echo "========================================="
echo ""

# Execute the setup script
echo "Running snowflake_setup.sql..."
snow sql -f snowflake_setup.sql

echo ""
echo "✅ Setup script executed successfully"
echo ""

echo "========================================="
echo "Step 3: Verify Installation"
echo "========================================="
echo ""

# Verify functions are created
echo "Checking created functions..."
snow sql -q "SHOW FUNCTIONS LIKE '%salesforce%' IN SCHEMA ${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA};"

echo ""
echo "========================================="
echo "Deployment Complete! 🎉"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Run tests: snow sql -f test_sfdc_tools.sql"
echo "2. Try querying accounts:"
echo "   snow sql -q \"SELECT salesforce_query_records('SELECT Id, Name FROM Account LIMIT 5');\""
echo ""
echo "See README.md for detailed usage instructions."
echo ""


#!/bin/bash
# ============================================================================
# GTME - GTM Engineer Agent Deployment Script
# ============================================================================
# Deploys Snowflake Cortex AI Agent with all integrations
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() { echo -e "\n${BLUE}=== $1 ===${NC}\n"; }
print_ok() { echo -e "${GREEN}✓ $1${NC}"; }
print_err() { echo -e "${RED}✗ $1${NC}"; }
print_warn() { echo -e "${YELLOW}! $1${NC}"; }

# ============================================================================
# Prerequisites
# ============================================================================
print_header "Checking Prerequisites"

if [ ! -f .env ]; then
    print_err ".env not found. Run: cp .env.example .env"
    exit 1
fi
source .env

command -v snow &>/dev/null || { print_err "Snow CLI not found. Run: pip install snowflake-cli-labs"; exit 1; }
command -v python3 &>/dev/null || command -v python &>/dev/null || { print_err "Python not found"; exit 1; }
PYTHON=$(command -v python3 || command -v python)

[ -z "$SNOWFLAKE_ACCOUNT" ] && { print_err "SNOWFLAKE_ACCOUNT not set in .env"; exit 1; }
[ -z "$SNOWFLAKE_PAT" ] && { print_err "SNOWFLAKE_PAT not set in .env"; exit 1; }

print_ok "Prerequisites OK"

# ============================================================================
# Step 1: Snowflake Infrastructure (run once)
# ============================================================================
print_header "Setting up Snowflake Infrastructure"

if [ "${SKIP_INFRA_SETUP:-false}" = "false" ]; then
    snow sql -f deployment/snowflake_setup.sql || print_warn "Infrastructure may already exist"
    print_ok "Infrastructure ready"
else
    print_warn "Skipping infrastructure setup (SKIP_INFRA_SETUP=true)"
fi

# ============================================================================
# Step 2: Deploy Tool Integrations
# ============================================================================
print_header "Deploying Tool Integrations"

# Google Workspace (if enabled)
if [ "${DEPLOY_GOOGLE_WORKSPACE:-true}" = "true" ]; then
    print_warn "Google Workspace requires manual OAuth setup first:"
    echo "  1. python tools/gsuite/get_oauth_url.py"
    echo "  2. python tools/gsuite/create_oauth_secret.py <refresh_token>"
fi

# Salesforce (if enabled)
if [ "${DEPLOY_SALESFORCE:-true}" = "true" ]; then
    print_header "Deploying Salesforce"
    snow sql -f tools/salesforce/snowflake_setup.sql
    print_ok "Salesforce deployed"
fi

# Web Search (if enabled)
if [ "${DEPLOY_WEB_SEARCH:-true}" = "true" ]; then
    print_header "Deploying Web Search"
    snow sql -f tools/web_search/perplexity/deploy_perplexity.sql
    snow sql -f tools/web_search/parallel_web_systems/deploy_findall.sql
    print_ok "Web Search deployed"
fi

# ============================================================================
# Create Agent
# ============================================================================
print_header "Creating Cortex AI Agent"

$PYTHON agent/build_agent.py gtm_engineer --delete

print_ok "Agent created successfully"

# ============================================================================
# Done
# ============================================================================
print_header "Deployment Complete!"

echo "Next Steps:"
echo "  1. Go to https://app.snowflake.com/"
echo "  2. Navigate to: AI & ML → Cortex → Agents"
echo "  3. Select: GTM_ENGINEER_AGENT"
echo "  4. Start chatting!"
echo ""
print_ok "Done!"


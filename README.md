# Snowflake GTM Agent

A Snowflake Cortex AI agent for Go-To-Market teams. Connects Salesforce, Google Workspace, and web search tools to automate CRM hygiene and pipeline building.

## What It Does

- **Salesforce**: Query/update accounts, opportunities, contacts
- **Google Workspace**: Create/read docs, sheets, drive files
- **Web Search**: Perplexity AI search + FindAll entity discovery

**Example**: "Read my meeting notes doc and update the Salesforce opportunity with the budget and next steps"

## Quick Start

```bash
git clone https://github.com/Roman-Gutin/snowflake-gtm-agent.git
cd snowflake-gtm-agent
cp .env.example .env    # Edit with your credentials
```

### Step 1: Snowflake Infrastructure (ACCOUNTADMIN)

```bash
snow sql -f deployment/snowflake_setup.sql
```

Creates: `AGENTS_DEMO` database, `AGENTS_DEMO_WH` warehouse, roles.

### Step 2: Deploy Integrations

**Salesforce:**
```bash
snow sql -f tools/salesforce/snowflake_setup.sql
```

**Web Search (Perplexity + FindAll):**
```bash
snow sql -f tools/web_search/perplexity/deploy_perplexity.sql
snow sql -f tools/web_search/parallel_web_systems/deploy_findall.sql
```

**Google Workspace** (requires OAuth):
```bash
python tools/gsuite/get_oauth_url.py          # Get auth URL
# Complete OAuth flow in browser
python tools/gsuite/create_oauth_secret.py    # Create Snowflake secret
```

### Step 3: Create Agent

```bash
python agent/build_agent.py gtm_engineer --delete
```

### Step 4: Use It

1. Go to [Snowsight](https://app.snowflake.com/)
2. Navigate to **AI & ML** → **Cortex** → **Agents**
3. Select **GTM_ENGINEER_AGENT**

## Repository Structure

```
snowflake-gtm-agent/
├── agent/
│   ├── build_agent.py              # Creates the Cortex agent
│   ├── configs/gtm_engineer.py     # Agent config (model, instructions)
│   └── tool_specs/                 # Tool definitions for the agent
│       ├── gsuite_tools.py
│       ├── salesforce_tools.py
│       ├── perplexity_tools.py
│       └── parallel_web_tools.py
│
├── deployment/
│   └── snowflake_setup.sql         # Base infrastructure (run first)
│
├── tools/
│   ├── gsuite/                     # Google Docs, Sheets, Drive
│   │   ├── handlers/               # Python handlers for UDFs
│   │   └── *.py                    # OAuth setup scripts
│   │
│   ├── salesforce/                 # Accounts, Opportunities, Contacts
│   │   ├── salesforce_tools/       # Python handlers
│   │   └── *.sql                   # UDF deployment
│   │
│   └── web_search/
│       ├── perplexity/             # AI-powered search
│       └── parallel_web_systems/   # FindAll entity discovery
│
├── deploy.sh / deploy.bat          # Full deployment scripts
└── .env.example                    # Credentials template
```

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                  Snowflake Account                      │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │      Cortex AI Agent (Claude Sonnet 4)            │ │
│  │  • Understands natural language requests          │ │
│  │  • Decides which tools to call                    │ │
│  └─────────────────────┬─────────────────────────────┘ │
│                        │                                │
│  ┌─────────────────────▼─────────────────────────────┐ │
│  │         Snowpark Python UDFs                      │ │
│  │  • CREATE_GOOGLE_DOC(), READ_GOOGLE_DOC()        │ │
│  │  • SALESFORCE_QUERY(), SALESFORCE_UPDATE()       │ │
│  │  • PERPLEXITY_SEARCH(), CREATE_FINDALL_RUN()     │ │
│  └─────────────────────┬─────────────────────────────┘ │
│                        │                                │
│  ┌─────────────────────▼─────────────────────────────┐ │
│  │    External Access Integrations                   │ │
│  │  • Network rules (allowed API endpoints)          │ │
│  │  • Secrets (OAuth tokens, API keys)               │ │
│  └─────────────────────┬─────────────────────────────┘ │
└────────────────────────┼────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Google   │   │Salesforce│   │ Web APIs │
   │ APIs     │   │ API      │   │          │
   └──────────┘   └──────────┘   └──────────┘
```

## Integration Setup

### Salesforce

Edit `tools/salesforce/snowflake_setup.sql` and update secrets:
```sql
CREATE SECRET salesforce_username TYPE = GENERIC_STRING SECRET_STRING = 'your-email@example.com';
CREATE SECRET salesforce_password TYPE = GENERIC_STRING SECRET_STRING = 'your-password';
CREATE SECRET salesforce_token TYPE = GENERIC_STRING SECRET_STRING = 'your-security-token';
```

Get security token: Salesforce → Setup → My Personal Information → Reset Security Token

### Perplexity

Edit `tools/web_search/perplexity/deploy_perplexity.sql`:
```sql
CREATE SECRET perplexity_api_key TYPE = GENERIC_STRING SECRET_STRING = 'pplx-xxxx';
```

Get API key: https://perplexity.ai/settings/api

### Parallel Web Systems (FindAll)

Edit `tools/web_search/parallel_web_systems/deploy_findall.sql`:
```sql
CREATE SECRET findall_api_key TYPE = GENERIC_STRING SECRET_STRING = 'your-api-key';
```

### Google Workspace

Requires OAuth flow:

1. Create OAuth app in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Enable: Google Docs API, Google Sheets API, Google Drive API
3. Run: `python tools/gsuite/get_oauth_url.py`
4. Complete browser auth flow
5. Run: `python tools/gsuite/create_oauth_secret.py`

## Adding New Integrations

1. Create tool specs in `agent/tool_specs/{integration}_tools.py`
2. Create handlers in `tools/{integration}/handlers/`
3. Create deployment SQL in `tools/{integration}/deploy_*.sql`
4. Add to `agent/configs/gtm_engineer.py`
5. Rebuild: `python agent/build_agent.py gtm_engineer --delete`

## Requirements

- Snowflake account with ACCOUNTADMIN
- Python 3.8+
- Snowflake CLI: `pip install snowflake-cli-labs`

## License

MIT
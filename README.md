# GTME - Go-To-Market Engineer AI Agent

> **Automate CRM hygiene with AI.** Deploy a Snowflake Cortex AI agent with Google Workspace, Salesforce, and Web Search integrations.

An AI agent that connects to the tools sellers actually use—Google Docs, Sheets, Drive, Salesforce, and web search—to automate the tedious work of keeping your CRM up to date and building pipeline.

## ⚡ Quick Start

```bash
git clone https://github.com/Roman-Gutin/GTME.git
cd GTME
cp .env.example .env
# Edit .env with your credentials

# Deploy (Linux/Mac)
./deploy.sh

# Deploy (Windows)
deploy.bat
```

## 🎯 What You Get

**Google Workspace Tools (22):**
- **Google Docs** (5): Create, read, insert, append, delete
- **Google Sheets** (6): Create, read, write, append, clear, delete
- **Google Drive** (11): List, search, create folders, share, permissions, export

**Salesforce Tools (11):**
- **Accounts**: Query, create, update, get details
- **Opportunities**: Query, create, update, get details
- **Discovery**: List objects, describe fields

**Web Search Tools (8):**
- **Perplexity**: AI-powered web search
- **FindAll**: Parallel entity discovery for prospecting (create, status, results, extend, enrich, cancel, manage)

**Use Cases:**
- Build pipeline by finding companies hosting events in your target market
- Extract action items from meeting notes → Update Salesforce
- Generate pipeline reports in Google Sheets
- Create customer proposals from templates
- Research prospects and enrich Salesforce records

## 🏗️ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Snowflake Account                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Cortex AI Agent (Claude Sonnet 4)            │  │
│  │  - Orchestrates tool calls                           │  │
│  │  - Maintains conversation context                    │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │ Calls tools                                 │
│               ▼                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Snowpark Python UDFs (Tools)                 │  │
│  │  - Google Docs: CREATE_GOOGLE_DOC()                  │  │
│  │  - Google Sheets: CREATE_GOOGLE_SHEET()              │  │
│  │  - Salesforce: QUERY_SALESFORCE_ACCOUNTS()           │  │
│  │  - 33 total UDFs registered                          │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │ Uses External Access                        │
│               ▼                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      External Access Integrations                    │  │
│  │  - Network rules (allowed endpoints)                 │  │
│  │  - Secrets (OAuth tokens, API keys)                  │  │
│  │  - Enables UDFs to call external APIs                │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
└───────────────┼─────────────────────────────────────────────┘
                │
                ▼
    ┌───────────────────────┐      ┌──────────────────────┐
    │   Google Workspace    │      │     Salesforce       │
    │   - Docs API          │      │   - REST API         │
    │   - Sheets API        │      │   - SOQL queries     │
    │   - Drive API         │      │   - CRUD operations  │
    └───────────────────────┘      └──────────────────────┘
```

### Key Components

1. **Personal Access Token (PAT)**
   - Required to authenticate REST API calls to create/manage agents
   - Service user (`AGENT_SERVICE_USER`) needs network policy to use PAT
   - Created via: `ALTER USER AGENT_SERVICE_USER ADD PROGRAMMATIC ACCESS TOKEN`

2. **Snowpark Python UDFs**
   - Python functions that run inside Snowflake
   - Can be called as SQL functions: `SELECT CREATE_GOOGLE_DOC('My Doc')`
   - Can be used as AI agent tools via tool specifications
   - Uploaded to Snowflake stage as `.py` files

3. **External Access Integrations**
   - Allow UDFs to make HTTP requests to external APIs
   - Require network rules (whitelist of allowed endpoints)
   - Can attach secrets for authentication
   - Example: `GOOGLE_EXTERNAL_ACCESS` allows calls to `*.googleapis.com`

4. **Tool Specifications (JSON)**
   - Define how the agent uses UDFs as tools
   - Include: function name, description, parameters, return type
   - Agent receives these specs and knows when/how to call each tool
   - Example:
     ```json
     {
       "type": "FUNCTION",
       "function": {
         "name": "CREATE_GOOGLE_DOC",
         "description": "Creates a new Google Doc",
         "parameters": {
           "type": "object",
           "properties": {
             "title": {"type": "string", "description": "Document title"}
           }
         }
       }
     }
     ```

5. **Agent Deployment via REST API**
   - Agents are created via POST to Snowflake REST API
   - Must be in `snowflake_intelligence.agents` schema to appear in Snowsight UI
   - Configuration includes:
     - Tools (tool specs + UDF references)
     - Model (Claude Sonnet 4)
     - Instructions (system prompt)
     - Response format

---

### RBAC Model

This system implements enterprise-grade security using Snowflake's Role-Based Access Control (RBAC).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Snowflake Account                                             │
│                                                                                                  │
│  ┌────────────────────────────────────┐          ┌──────────────────────────────────────────┐  │
│  │      ACCOUNTADMIN Role             │          │         AGENTS_DEMO Database             │  │
│  │  - Creates infrastructure          │──────────│  - Owned by AGENTS_SERVICE_ROLE          │  │
│  │  - Grants permissions              │  Creates │  - Contains: PUBLIC schema               │  │
│  └────────────┬───────────────────────┘          │             AGENTS_STAGE                 │  │
│               │                                  │             33 UDFs                      │  │
│               │ GRANT ROLE                       │             Secrets                      │  │
│               │ AGENTS_SERVICE_ROLE              │             External Access Integrations │  │
│               │ TO USER                          └──────────────────────────────────────────┘  │
│               │ AGENT_SERVICE_USER                                                             │
│               ▼                                                                                │
│  ┌────────────────────────────────────┐          ┌──────────────────────────────────────────┐  │
│  │     AGENTS_SERVICE_ROLE            │          │         Key Grants                       │  │
│  │  - Owns all infrastructure         │◄─────────│  USAGE on AGENTS_DEMO                    │  │
│  │  - CREATE FUNCTION                 │  Owns    │  USAGE on AGENTS_WH                      │  │
│  │  - USAGE on integrations           │          │  CREATE FUNCTION on PUBLIC               │  │
│  │  - READ on secrets                 │          │  USAGE on GOOGLE_EXTERNAL_ACCESS         │  │
│  │  - EXECUTE on UDFs                 │          │  USAGE on SALESFORCE_EXTERNAL_ACCESS     │  │
│  └────────────┬───────────────────────┘          │  READ on google_oauth_secret             │  │
│               │                                  │  READ on salesforce_username             │  │
│               │ Assigned to                      │  EXECUTE on all 33 UDFs                  │  │
│               ▼                                  └──────────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐                                                        │
│  │   AGENT_SERVICE_USER (SERVICE)     │          ┌──────────────────────────────────────────┐  │
│  │  - Executes agent operations       │          │      AGENTS_WH Warehouse                 │  │
│  │  - Uses PAT for REST API           │──────────│  - Owned by AGENTS_SERVICE_ROLE          │  │
│  │  - Requires network policy         │  Uses    │  - Size: X-SMALL                         │  │
│  │  - Runs UDFs                       │          │  - Auto-suspend: 60 seconds              │  │
│  └────────────────────────────────────┘          └──────────────────────────────────────────┘  │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Key Security Components

**1. Service User (AGENT_SERVICE_USER)**
- **Type:** SERVICE (not a human user)
- **Purpose:** Execute agent operations and UDFs
- **Authentication:** Personal Access Token (PAT)
- **Network Policy:** Required for PAT usage (security requirement)

**2. Service Role (AGENTS_SERVICE_ROLE)**
- **Owns:** Database, warehouse, stage, UDFs, secrets, integrations
- **Permissions:**
  - `USAGE` on database and warehouse
  - `CREATE FUNCTION` on schema
  - `USAGE` on external access integrations
  - `READ` on secrets
  - `EXECUTE` on all UDFs

**3. Separation of Duties**
- **ACCOUNTADMIN:** Sets up infrastructure (one-time)
- **AGENTS_SERVICE_ROLE:** Owns and operates agent resources
- **AGENT_SERVICE_USER:** Executes operations (no direct login)

**4. Network Policy**
```sql
CREATE NETWORK POLICY AGENTS_SERVICE_NETWORK_POLICY
  ALLOWED_IP_LIST = ('0.0.0.0/0')  -- Adjust for production
  COMMENT = 'Required for service user to use PAT';

ALTER USER AGENT_SERVICE_USER
  SET NETWORK_POLICY = AGENTS_SERVICE_NETWORK_POLICY;
```

**Why this matters:**
- Service users (TYPE=SERVICE) **cannot** use PAT without a network policy
- Network policy defines allowed IP ranges for authentication
- In production, restrict to specific IP ranges or VPCs

**5. Secret Management**
```sql
-- Secrets are owned by AGENTS_SERVICE_ROLE
CREATE SECRET google_oauth_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = '<oauth_refresh_token>';

-- Only AGENTS_SERVICE_ROLE can read
GRANT READ ON SECRET google_oauth_secret
  TO ROLE AGENTS_SERVICE_ROLE;
```

**6. External Access Control**
```sql
-- External access integrations are owned by AGENTS_SERVICE_ROLE
CREATE EXTERNAL ACCESS INTEGRATION GOOGLE_EXTERNAL_ACCESS
  ALLOWED_NETWORK_RULES = (google_apis_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (google_oauth_secret);

-- Only AGENTS_SERVICE_ROLE can use
GRANT USAGE ON INTEGRATION GOOGLE_EXTERNAL_ACCESS
  TO ROLE AGENTS_SERVICE_ROLE;
```

#### Production Hardening

**For production deployments, consider:**

1. **Restrict network policy:**
   ```sql
   CREATE NETWORK POLICY AGENTS_SERVICE_NETWORK_POLICY
     ALLOWED_IP_LIST = ('203.0.113.0/24')  -- Your VPC CIDR
     BLOCKED_IP_LIST = ('0.0.0.0/0');
   ```

2. **Rotate PAT regularly:**
   ```sql
   -- Revoke old token
   ALTER USER AGENT_SERVICE_USER DROP PROGRAMMATIC ACCESS TOKEN old_token;

   -- Create new token
   ALTER USER AGENT_SERVICE_USER ADD PROGRAMMATIC ACCESS TOKEN new_token;
   ```

3. **Audit access:**
   ```sql
   -- Query access history
   SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
   WHERE USER_NAME = 'AGENT_SERVICE_USER'
   ORDER BY QUERY_START_TIME DESC;
   ```

4. **Separate environments:**
   - Dev: `AGENTS_DEMO` database
   - Prod: `AGENTS_PROD` database
   - Different service users per environment

---

## 📋 Prerequisites

- **Snowflake account** with ACCOUNTADMIN role
- **Python 3.8+** installed
- **Snowflake CLI** installed: `pip install snowflake-cli-labs`
- **Integration credentials** (choose what you need):
  - Google Cloud OAuth 2.0 (for Google Workspace)
  - Salesforce username/password/token (for Salesforce)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Roman-Gutin/GTME.git
cd GTME
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env
```

**Edit `.env` and configure:**

**Required (all deployments):**
- `SNOWFLAKE_ACCOUNT` - Your Snowflake account identifier
- `DEPLOY_GOOGLE_WORKSPACE` - Set to `true` or `false`
- `DEPLOY_SALESFORCE` - Set to `true` or `false`

**For Google Workspace** (if `DEPLOY_GOOGLE_WORKSPACE=true`):
- `GOOGLE_CLIENT_ID` - From Google Cloud Console
- `GOOGLE_CLIENT_SECRET` - From Google Cloud Console

**For Salesforce** (if `DEPLOY_SALESFORCE=true`):
- `SALESFORCE_USERNAME` - Your Salesforce username
- `SALESFORCE_PASSWORD` - Your Salesforce password
- `SALESFORCE_SECURITY_TOKEN` - Your Salesforce security token

### 3. Get Integration Credentials

<details>
<summary><b>Google Workspace Setup</b> (click to expand)</summary>

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing
3. Enable APIs: **Google Docs API**, **Google Sheets API**, **Google Drive API**
4. Create **OAuth 2.0 Client ID**:
   - Application type: **Desktop app**
   - Name: `GTME Agent`
5. Copy **Client ID** and **Client Secret** to `.env`

</details>

<details>
<summary><b>Salesforce Setup</b> (click to expand)</summary>

1. Log in to Salesforce
2. Go to **Setup** → **My Personal Information** → **Reset Security Token**
3. Check your email for the security token
4. Add to `.env`:
   - `SALESFORCE_USERNAME`: Your Salesforce login email
   - `SALESFORCE_PASSWORD`: Your Salesforce password
   - `SALESFORCE_SECURITY_TOKEN`: Token from email

</details>

### 4. Run Deployment

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

The script will:
1. ✅ Validate prerequisites and check credentials
2. ✅ Deploy Salesforce UDFs (if enabled)
3. ✅ Deploy Web Search UDFs (Perplexity + FindAll, if enabled)
4. ✅ Create the GTME Cortex AI Agent with all tools

**Note:** Google Workspace requires manual OAuth setup:
```bash
python tools/gsuite/get_oauth_url.py
python tools/gsuite/create_oauth_secret.py <refresh_token>
```

### 5. Access Your Agent

1. Go to [Snowsight](https://app.snowflake.com/)
2. Navigate to **AI & ML** → **Cortex** → **Agents**
3. Select **GTM_ENGINEER_AGENT**
4. Start chatting!

**Example prompts:**

<details>
<summary><b>Google Workspace Examples</b></summary>

```
Create a Google Doc called "Meeting Notes" with an agenda section

Create a Google Sheet called "Sales Pipeline" with columns:
Company, Contact, Stage, Amount, Close Date

Create a folder in Google Drive called "Q1 2025 Reports" and
share it with team@company.com

Search my Drive for all PDFs modified in the last week
```

</details>

<details>
<summary><b>Salesforce Examples</b></summary>

```
Show me all opportunities closing this quarter

Get details for account "Acme Corporation"

Create a new opportunity for account 001xxx with amount $50,000

What's the total pipeline value for this quarter?

List all custom objects in my Salesforce org
```

</details>

<details>
<summary><b>Combined Workflow Examples</b></summary>

```
Pull the top 10 opportunities from Salesforce and create a
Google Sheet with their details

Create a Google Doc summarizing all accounts in the
"Negotiation" stage

For each opportunity closing this month, create a folder in
Google Drive with the account name
```

</details>

---

## 🔧 Technical Deep Dive

### Understanding the Infrastructure

#### 1. Personal Access Token (PAT) Setup

**Why PAT is needed:**
- Snowflake Cortex AI Agents are created via REST API, not SQL
- REST API requires authentication via Personal Access Token
- Service users (TYPE=SERVICE) need a network policy to use PATs

**What the deployment does:**
```sql
-- Create service user
CREATE USER AGENT_SERVICE_USER TYPE = SERVICE;

-- Create network policy (required for PAT usage)
CREATE NETWORK POLICY AGENTS_SERVICE_NETWORK_POLICY
  ALLOWED_IP_LIST = ('0.0.0.0/0');

-- Attach policy to user
ALTER USER AGENT_SERVICE_USER
  SET NETWORK_POLICY = AGENTS_SERVICE_NETWORK_POLICY;

-- Generate PAT (done via Snow CLI)
snow sql -q "ALTER USER AGENT_SERVICE_USER
  ADD PROGRAMMATIC ACCESS TOKEN gtme_agent_token;"
```

**How it's used:**
```python
# In agent/api_client.py
headers = {
    "Authorization": f"Bearer {pat_token}",
    "Content-Type": "application/json"
}
response = requests.post(
    f"https://{account}.snowflakecomputing.com/api/v2/databases/..."
)
```

---

#### 2. Snowpark Python UDFs as Tools

**What are Snowpark UDFs?**
- Python functions that run inside Snowflake's compute environment
- Can import packages (via Anaconda or uploaded files)
- Can make HTTP requests (via External Access Integrations)
- Can be called as SQL functions OR used as AI agent tools

**Example: Google Docs UDF**

Handler file (`tools/gsuite/handlers/docs_handler.py`):
```python
def create_google_doc(title: str, content: str = "") -> str:
    import _snowflake
    import requests

    # Get OAuth token from secret
    token = _snowflake.get_generic_secret_string('google_oauth_secret')

    # Call Google Docs API
    response = requests.post(
        'https://docs.googleapis.com/v1/documents',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': title}
    )
    return response.json()['documentId']
```

UDF registration (generated by `deployment/create_udfs.py`):
```sql
CREATE OR REPLACE FUNCTION CREATE_GOOGLE_DOC(title STRING, content STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('requests', 'snowflake-snowpark-python')
IMPORTS = ('@gtme_stage/docs_handler.py')
HANDLER = 'docs_handler.create_google_doc'
EXTERNAL_ACCESS_INTEGRATIONS = (GOOGLE_EXTERNAL_ACCESS)
SECRETS = ('google_oauth_secret' = google_oauth_secret);
```

**Dual usage:**

As SQL function:
```sql
SELECT CREATE_GOOGLE_DOC('My Document', 'Hello World');
-- Returns: document_id
```

As AI agent tool:
- Agent receives tool specification (JSON)
- Agent decides when to call the tool
- Agent calls: `CREATE_GOOGLE_DOC('Meeting Notes', '')`
- UDF executes and returns result

---

#### 3. External Access Integrations

**Purpose:**
- By default, Snowpark UDFs cannot make HTTP requests
- External Access Integrations whitelist allowed endpoints
- Can attach secrets for authentication

**Example: Google Workspace**

Network rule (allowed endpoints):
```sql
CREATE OR REPLACE NETWORK RULE google_apis_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = (
    'docs.googleapis.com:443',
    'sheets.googleapis.com:443',
    'www.googleapis.com:443'
  );
```

External access integration:
```sql
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION GOOGLE_EXTERNAL_ACCESS
  ALLOWED_NETWORK_RULES = (google_apis_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (google_oauth_secret)
  ENABLED = TRUE;
```

Attached to UDF:
```sql
CREATE FUNCTION CREATE_GOOGLE_DOC(...)
...
EXTERNAL_ACCESS_INTEGRATIONS = (GOOGLE_EXTERNAL_ACCESS)
SECRETS = ('google_oauth_secret' = google_oauth_secret);
```

**How it works:**
1. UDF calls `requests.post('https://docs.googleapis.com/...')`
2. Snowflake checks: Is `docs.googleapis.com` in allowed rules? ✅
3. UDF accesses secret: `_snowflake.get_generic_secret_string(...)`
4. Request made with OAuth token
5. Response returned to UDF, then to agent

---

#### 4. Tool Specifications

**What are tool specs?**
- JSON definitions that tell the agent how to use each UDF
- Include: function name, description, parameters, return type
- Agent uses these to decide when and how to call tools

**Example:** `tools/gsuite/specs/docs_tools.json`
```json
{
  "type": "FUNCTION",
  "function": {
    "name": "CREATE_GOOGLE_DOC",
    "description": "Creates a new Google Document",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The title of the new document"
        }
      },
      "required": ["title"]
    }
  }
}
```

**How agent uses it:**
1. User: "Create a doc called Meeting Notes"
2. Agent: "I need CREATE_GOOGLE_DOC tool"
3. Agent calls: `CREATE_GOOGLE_DOC(title='Meeting Notes')`
4. UDF executes, returns document ID
5. Agent responds with result

---

#### 5. Agent Deployment via REST API

**Why REST API?**
- Cortex AI Agents cannot be created via SQL (yet)
- Must use Snowflake REST API
- Requires Personal Access Token authentication

**Endpoint:**
```
POST https://{account}.snowflakecomputing.com/api/v2/
     databases/{db}/schemas/{schema}/agents/{name}
```

**Request body:**
```json
{
  "tools": [
    {
      "tool_spec": {
        "type": "FUNCTION",
        "function": {
          "name": "CREATE_GOOGLE_DOC",
          "description": "Creates a new Google Document",
          "parameters": { ... }
        }
      },
      "tool_resource": {
        "type": "FUNCTION",
        "function": { "name": "CREATE_GOOGLE_DOC" }
      }
    }
  ],
  "orchestration": {
    "model": "claude-sonnet-4",
    "instructions": "You are a GTM Engineer..."
  }
}
```

**Key points:**
- `tool_spec`: JSON definition (what agent sees)
- `tool_resource`: UDF reference (what gets executed)
- Must be in `snowflake_intelligence.agents` schema for Snowsight UI

**What deployment does:**
```python
# In agent/create_agent.py
from agent.tool_registry import ToolRegistry

# Load all tool specs from JSON files
registry = ToolRegistry()
registry.discover_tools()  # Finds tools/*/specs/*.json

# Create agent via REST API
client.create_agent(
    name="GTM_ENGINEER_AGENT",
    tools=registry.get_all_tools(),
    model="claude-sonnet-4"
)
```

---

## 📁 Repository Structure

```
GTME/
├── agent/                          # Agent creation and management
│   ├── build_agent.py             # Main agent builder script
│   ├── configs/                   # Agent configurations
│   │   └── gtm_engineer.py        # GTM Engineer agent config
│   └── tool_specs/                # Tool specifications (Python)
│       ├── gsuite_tools.py        # Google Workspace tool specs
│       ├── salesforce_tools.py    # Salesforce tool specs
│       ├── perplexity_tools.py    # Perplexity search tool specs
│       └── parallel_web_tools.py  # FindAll web search tool specs
│
├── tools/                          # Tool integrations
│   ├── gsuite/                    # Google Workspace (22 tools)
│   │   ├── handlers/              # Python API wrappers
│   │   ├── get_oauth_url.py       # OAuth URL generator
│   │   ├── generate_oauth_token.py # Token generator
│   │   └── create_oauth_secret.py # Secret creation
│   │
│   ├── salesforce/                # Salesforce CRM (11 tools)
│   │   ├── salesforce_tools/      # Python API wrappers
│   │   ├── deploy_*.sql           # UDF deployment scripts
│   │   └── snowflake_setup.sql    # Infrastructure setup
│   │
│   └── web_search/                # Web search tools
│       ├── perplexity/            # Perplexity AI search
│       │   ├── handlers/          # Python handler
│       │   └── deploy_perplexity.sql
│       └── parallel_web_systems/  # FindAll entity discovery
│           ├── handlers/          # Python handler
│           └── deploy_*.sql       # UDF deployment scripts
│
├── deploy.sh                       # Master deployment (Linux/Mac)
├── deploy.bat                      # Master deployment (Windows)
├── .env.example                    # Environment template
└── README.md                       # This file
```

---

## 🔄 Agent Workflow Example: CRM Hygiene Automation

### Scenario: Update Salesforce from Meeting Notes

**User prompt:**
> "Read the meeting notes from the Google Doc titled 'Acme Corp - Discovery Call 2024-01-15' and update the Salesforce opportunity"

**Agent execution flow:**

#### Step 1: Read Google Doc
```
Agent thinks: "I need to find and read the Google Doc"

Tool call: SEARCH_GOOGLE_DRIVE_FILES
Parameters: {
  "query": "Acme Corp - Discovery Call 2024-01-15",
  "file_type": "document"
}
Returns: { "file_id": "1abc...xyz", "name": "Acme Corp - Discovery Call 2024-01-15" }

Tool call: READ_GOOGLE_DOC
Parameters: { "document_id": "1abc...xyz" }
Returns: {
  "content": "Meeting with John Smith, CTO at Acme Corp.
              Budget: $150K confirmed
              Timeline: Q2 2024 implementation
              Next steps: Send proposal by Friday
              Decision makers: John Smith (CTO), Sarah Johnson (VP Eng)
              Pain points: Current system lacks API integrations..."
}
```

#### Step 2: Find Salesforce Opportunity
```
Agent thinks: "I need to find the Acme Corp opportunity in Salesforce"

Tool call: SEARCH_SALESFORCE_OPPORTUNITIES
Parameters: { "account_name": "Acme Corp" }
Returns: {
  "opportunities": [
    {
      "id": "006...abc",
      "name": "Acme Corp - Enterprise License",
      "stage": "Discovery",
      "amount": null,
      "close_date": null
    }
  ]
}
```

#### Step 3: Update Opportunity
```
Agent thinks: "I'll update the opportunity with budget, timeline, and next steps"

Tool call: UPDATE_SALESFORCE_OPPORTUNITY
Parameters: {
  "opportunity_id": "006...abc",
  "fields": {
    "Amount": 150000,
    "CloseDate": "2024-06-30",
    "StageName": "Proposal",
    "NextStep": "Send proposal by Friday",
    "Description": "Budget: $150K confirmed. Timeline: Q2 2024.
                    Decision makers: John Smith (CTO), Sarah Johnson (VP Eng).
                    Pain points: Current system lacks API integrations."
  }
}
Returns: { "success": true, "id": "006...abc" }
```

#### Step 4: Update Account
```
Agent thinks: "I should also update the account with the decision makers"

Tool call: GET_SALESFORCE_ACCOUNT
Parameters: { "account_name": "Acme Corp" }
Returns: { "id": "001...xyz", "name": "Acme Corp" }

Tool call: UPDATE_SALESFORCE_ACCOUNT
Parameters: {
  "account_id": "001...xyz",
  "fields": {
    "Description": "Key contacts: John Smith (CTO), Sarah Johnson (VP Eng).
                    Pain points: API integration gaps."
  }
}
Returns: { "success": true, "id": "001...xyz" }
```

#### Agent Response
```
✅ I've updated your Salesforce records based on the meeting notes:

Opportunity: Acme Corp - Enterprise License
- Amount: $150,000
- Close Date: June 30, 2024
- Stage: Proposal (moved from Discovery)
- Next Step: Send proposal by Friday
- Added decision makers and pain points to description

Account: Acme Corp
- Updated with key contacts (John Smith - CTO, Sarah Johnson - VP Eng)
- Documented pain points around API integrations

Total: 4 tool calls, 2 systems updated automatically
```

**What just happened:**
1. Agent read unstructured meeting notes from Google Docs
2. Extracted structured data (budget, timeline, contacts, pain points)
3. Found the correct Salesforce opportunity
4. Updated opportunity with new information and moved stage forward
5. Updated account with decision maker information
6. All without manual data entry

**This is CRM hygiene automation in action.**

---

## 🧪 Testing Your Deployment

### Verify Infrastructure

```bash
snow sql -f deployment/test_deployment.sql
```

**Checks:**
- ✅ Snowflake stage created
- ✅ Python files uploaded
- ✅ External access integrations configured
- ✅ Secrets created
- ✅ UDFs registered
- ✅ Agent created

### Test Google Workspace Tools

```bash
snow sql -f deployment/test_tools.sql
```

**Tests all 22 tools:**
- Creates test documents, sheets, folders
- Performs CRUD operations
- Verifies sharing and permissions
- Cleans up test data

### Test Salesforce Tools

```bash
snow sql -f tools/salesforce/test_sfdc_tools.sql
```

**Tests all 11 tools:**
- Queries accounts and opportunities
- Creates test records
- Updates and retrieves data
- Tests discovery functions

---

## 🔧 Troubleshooting

<details>
<summary><b>Snow CLI not found</b></summary>

**Error:** `snow: command not found`

**Solution:**
```bash
pip install snowflake-cli-labs
```

Verify installation:
```bash
snow --version
```

</details>

<details>
<summary><b>Google OAuth authorization failed</b></summary>

**Error:** `Invalid OAuth credentials` or `Redirect URI mismatch`

**Solution:**
1. Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
2. Check redirect URI in Google Cloud Console is `http://localhost:8080`
3. Ensure APIs are enabled: Docs, Sheets, Drive
4. Try generating a new OAuth token:
   ```bash
   python tools/gsuite/get_oauth_url.py
   ```

</details>

<details>
<summary><b>Salesforce authentication failed</b></summary>

**Error:** `INVALID_LOGIN` or `Authentication failure`

**Solution:**
1. Verify credentials in `.env`:
   - `SALESFORCE_USERNAME` - Your Salesforce email
   - `SALESFORCE_PASSWORD` - Your password
   - `SALESFORCE_SECURITY_TOKEN` - From email (reset if needed)
2. Reset security token: Setup → My Personal Information → Reset Security Token
3. Update secrets in Snowflake:
   ```bash
   snow sql -q "ALTER SECRET salesforce_username SET SECRET_STRING = 'your-email@salesforce.com';"
   ```

</details>

<details>
<summary><b>Agent not visible in Snowsight</b></summary>

**Error:** Agent created but not showing in UI

**Solution:**
1. Verify agent is in correct schema:
   ```bash
   snow sql -q "SHOW AGENTS IN SCHEMA snowflake_intelligence.agents;"
   ```
2. Check you're using the correct role: `AGENTS_SERVICE_ROLE`
3. Refresh Snowsight browser page
4. Navigate to: AI & ML → Cortex → Agents

</details>

<details>
<summary><b>UDF creation failed</b></summary>

**Error:** `Function already exists` or `Import path not found`

**Solution:**
1. Verify stage has files:
   ```bash
   snow sql -q "LIST @AGENTS_DEMO.PUBLIC.GSUITE_STAGE;"
   ```
2. Drop and recreate UDFs:
   ```bash
   python deployment/create_udfs.py
   ```
3. Check external access integration exists:
   ```bash
   snow sql -q "SHOW EXTERNAL ACCESS INTEGRATIONS;"
   ```

</details>

---

## 🔄 Adding New Integrations

The architecture is designed to be extensible. To add new tools (e.g., HubSpot, Slack, Jira):

1. **Create tool specifications** in `agent/tool_specs/{integration}_tools.py`
2. **Implement Python handlers** in `tools/{integration}/handlers/`
3. **Create SQL deployment script** in `tools/{integration}/deploy_*.sql`
4. **Add to master deployment** in `deploy.sh` and `deploy.bat`
5. **Update agent configuration** in `agent/configs/gtm_engineer.py`

See `tools/gsuite/` for reference implementation.

Run `python agent/build_agent.py gtm_engineer --delete` to rebuild the agent.

---

## 📚 Additional Documentation

### Integration-Specific Guides

- **Google Workspace**: See `tools/gsuite/` for OAuth setup and handler details
- **Salesforce**: See `tools/salesforce/README.md` for detailed Salesforce setup
- **Deployment Guide**: See `tools/salesforce/DEPLOYMENT_GUIDE.md` for advanced options

### Reference Documentation

- [Snowflake Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-ai)
- [Google Workspace API Documentation](https://developers.google.com/workspace)
- [Salesforce API Documentation](https://developer.salesforce.com/docs/apis)
- [Refactoring Status](REFACTORING_STATUS.md) - Implementation details

---

## 🎯 What's Next?

After successful deployment, you can:

1. **Customize the agent** - Edit `agent/config.py` to modify instructions
2. **Add more tools** - Follow the extensible architecture pattern
3. **Create workflows** - Combine tools for complex automation
4. **Monitor usage** - Check execution logs in Snowflake
5. **Scale up** - Deploy to production with proper RBAC

---

## 💡 Use Cases

### Sales & Marketing
- Auto-generate sales proposals in Google Docs from Salesforce opportunities
- Create pipeline reports in Google Sheets from Salesforce data
- Sync meeting notes from Google Docs to Salesforce accounts

### Operations
- Automated folder creation in Drive for new Salesforce accounts
- Weekly pipeline summaries emailed via Google Workspace
- Document generation for contract management

### Analytics
- Pull Salesforce data into Google Sheets for analysis
- Create executive dashboards combining both platforms
- Automated reporting workflows

---

## 🤝 Contributing

Contributions welcome! This repository demonstrates a clean, modular architecture for Snowflake Cortex AI Agents that can serve as a reference implementation.

**Areas for contribution:**
- Additional integrations (HubSpot, Slack, Jira, etc.)
- Enhanced tool specifications
- Improved error handling
- Documentation improvements

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- **Snowflake Cortex AI** - Agent orchestration
- **Claude Sonnet 4** - Language model
- **Google Workspace APIs** - Productivity tools
- **Salesforce APIs** - CRM integration

---
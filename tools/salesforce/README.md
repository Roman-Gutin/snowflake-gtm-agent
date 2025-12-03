# Salesforce Tools for Snowflake

Production-ready Salesforce integration tools deployable as Snowflake UDFs for Cortex Agents.

## 🎯 Overview

This package provides reliable Salesforce data operations through Snowflake UDFs. **Note:** Schema operations (creating fields/objects) must be done via Salesforce UI - only data operations are supported via API.

## ✨ What Works (Data Operations)

✅ **Query & Read** - SOQL queries, get records, search  
✅ **Create & Update** - Insert/update records  
✅ **Delete** - Remove records  
✅ **Discovery** - List objects, describe metadata  
✅ **Shortcuts** - Account, Contact, Opportunity helpers  

❌ **What Doesn't Work via API:**
- Creating custom fields (use Salesforce UI)
- Creating custom objects (use Salesforce UI)
- Modifying page layouts (use Salesforce UI)

## 📦 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Create `credentials.json`:

```json
{
  "username": "your-username@salesforce.com",
  "password": "your-password",
  "security_token": "your-security-token"
}
```

### 3. Deploy to Snowflake

```bash
# Windows
deploy_to_snowflake.bat

# Linux/Mac
./deploy_to_snowflake.sh
```

## 🚀 Quick Start

### Python Usage

```python
from salesforce_tools import SalesforceTools

# Initialize
sf = SalesforceTools(
    username="user@example.com",
    password="password",
    security_token="token"
)

# Query accounts
accounts = sf.query_accounts("SELECT Id, Name FROM Account LIMIT 10")

# Get account details
account = sf.get_account("001xxx")

# Create opportunity
opp_id = sf.create_opportunity({
    'Name': 'Q4 2025 - Enterprise Deal',
    'AccountId': '001xxx',
    'Amount': 250000,
    'CloseDate': '2025-12-31',
    'StageName': 'Prospecting'
})

# Update opportunity
sf.update_opportunity('006xxx', {
    'StageName': 'Negotiation',
    'Amount': 300000
})
```

### Snowflake Usage

```sql
-- Query accounts
SELECT salesforce_query_accounts('SELECT Id, Name, Industry FROM Account LIMIT 10');

-- Get account details
SELECT salesforce_get_account('001g5000002OccTAAS');

-- Create opportunity
SELECT salesforce_create_opportunity(OBJECT_CONSTRUCT(
    'Name', 'Q4 2025 Deal',
    'AccountId', '001xxx',
    'Amount', 250000,
    'CloseDate', '2025-12-31',
    'StageName', 'Prospecting'
));

-- Update opportunity
SELECT salesforce_update_opportunity('006xxx', OBJECT_CONSTRUCT(
    'StageName', 'Closed Won',
    'Amount', 300000
));

-- Search opportunities
SELECT salesforce_search_opportunities('DirectConsumerCo');
```

## 📚 Available Functions

### Query & Read Operations

| Function | Description | Example |
|----------|-------------|---------|
| `query_records(soql)` | Execute SOQL query | `query_records("SELECT Id FROM Account")` |
| `get_account(id)` | Get account by ID | `get_account("001xxx")` |
| `get_opportunity(id)` | Get opportunity by ID | `get_opportunity("006xxx")` |
| `get_contact(id)` | Get contact by ID | `get_contact("003xxx")` |
| `search_accounts(name)` | Search accounts by name | `search_accounts("Acme")` |
| `search_opportunities(keyword)` | Search opportunities | `search_opportunities("Enterprise")` |

### Create & Update Operations

| Function | Description | Example |
|----------|-------------|---------|
| `create_account(data)` | Create account | `create_account({'Name': 'Acme'})` |
| `create_opportunity(data)` | Create opportunity | `create_opportunity({...})` |
| `create_contact(data)` | Create contact | `create_contact({...})` |
| `update_account(id, data)` | Update account | `update_account('001xxx', {...})` |
| `update_opportunity(id, data)` | Update opportunity | `update_opportunity('006xxx', {...})` |
| `update_contact(id, data)` | Update contact | `update_contact('003xxx', {...})` |

### Delete Operations

| Function | Description | Example |
|----------|-------------|---------|
| `delete_record(object, id)` | Delete any record | `delete_record('Account', '001xxx')` |

### Discovery Operations

| Function | Description | Example |
|----------|-------------|---------|
| `list_objects()` | List all objects | `list_objects()` |
| `describe_object(name)` | Get object metadata | `describe_object('Account')` |
| `get_field_names(object)` | Get field names | `get_field_names('Opportunity')` |

## 🏗️ Project Structure

```
salesforce_clean/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── credentials.json.template    # Credentials template
├── deploy_to_snowflake.sh      # Deployment script (Unix)
├── deploy_to_snowflake.bat     # Deployment script (Windows)
├── snowflake.yml               # Snowpark config
├── snowflake_setup.sql         # UDF definitions
├── salesforce_tools/           # Main package
│   ├── __init__.py
│   ├── core.py                 # Core Salesforce operations
│   ├── accounts.py             # Account operations
│   ├── opportunities.py        # Opportunity operations
│   ├── contacts.py             # Contact operations
│   └── discovery.py            # Discovery operations
└── examples/                   # Usage examples
    ├── python_examples.py
    └── sql_examples.sql
```

## 🔧 Configuration

### Snowflake Configuration (`snowflake.yml`)

```yaml
connections:
  default:
    account: your-account
    user: your-user
    password: your-password
    role: your-role
    warehouse: your-warehouse
    database: your-database
    schema: your-schema
```

### Salesforce Credentials (`credentials.json`)

```json
{
  "username": "user@salesforce.com",
  "password": "your-password",
  "security_token": "your-token"
}
```

**Getting Security Token:**
1. Log into Salesforce
2. Settings → My Personal Information → Reset My Security Token
3. Check your email for the token

## 📖 Use Cases

### Use Case 1: Track Customer Opportunities

```sql
-- Get all opportunities for an account
SELECT salesforce_query_records(
    'SELECT Id, Name, Amount, StageName, CloseDate 
     FROM Opportunity 
     WHERE AccountId = ''001xxx'' 
     AND IsClosed = false'
);

-- Update opportunity stage
SELECT salesforce_update_opportunity('006xxx', 
    OBJECT_CONSTRUCT('StageName', 'Closed Won')
);
```

### Use Case 2: Sync Salesforce Data to Snowflake

```sql
-- Create table from Salesforce query
CREATE OR REPLACE TABLE salesforce_accounts AS
SELECT PARSE_JSON(salesforce_query_records(
    'SELECT Id, Name, Industry, AnnualRevenue, BillingCity, BillingState 
     FROM Account 
     WHERE Type = ''Customer'''
));

-- Schedule daily sync
CREATE OR REPLACE TASK sync_salesforce_accounts
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 2 * * * America/Los_Angeles'
AS
    INSERT OVERWRITE INTO salesforce_accounts
    SELECT PARSE_JSON(salesforce_query_records(
        'SELECT Id, Name, Industry, AnnualRevenue FROM Account'
    ));
```

### Use Case 3: Enrich Snowflake Data with Salesforce

```sql
-- Join Snowflake data with Salesforce accounts
SELECT 
    s.customer_name,
    s.revenue,
    PARSE_JSON(salesforce_get_account(s.salesforce_account_id)) as sf_data
FROM snowflake_customers s
WHERE s.salesforce_account_id IS NOT NULL;
```

## 🧪 Testing

```bash
# Test Python functions
python -m pytest tests/

# Test Snowflake UDFs
snowsql -f examples/sql_examples.sql
```

## 🚨 Important Notes

### What Works via API ✅
- **All data operations** (CRUD on records)
- **Queries** (SOQL)
- **Discovery** (listing objects, fields)

### What Requires Salesforce UI ⚠️
- **Creating custom fields** - Must use Salesforce Setup UI
- **Creating custom objects** - Must use Salesforce Setup UI
- **Modifying page layouts** - Must use Salesforce Setup UI
- **Creating validation rules** - Must use Salesforce Setup UI

**Why?** Salesforce's Metadata API is:
- Asynchronous and unreliable
- Complex authentication requirements
- Poor error handling
- Often fails silently

**Recommendation:** Use Salesforce UI for schema changes (one-time setup), then use these tools for all data operations.

## 📊 Performance

- **Query Performance:** ~100-500ms per query
- **Bulk Operations:** Use Salesforce Bulk API for >2000 records
- **Rate Limits:** 15,000 API calls per 24 hours (standard edition)

## 🔒 Security

- Credentials stored in Snowflake secrets (encrypted)
- OAuth 2.0 authentication
- Security token required for API access
- IP whitelisting recommended

## 📞 Support

For issues or questions:
1. Check examples in `examples/` directory
2. Review Salesforce API documentation
3. Test with `python_examples.py` first

## 📄 License

MIT License

---

**Built for production use with Snowflake Cortex Agents** 🚀


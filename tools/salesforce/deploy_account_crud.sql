-- ============================================================================
-- Salesforce Account CRUD Tools Deployment
-- ============================================================================
-- Deploys Account Create, Read, Update, Delete UDFs to Snowflake
-- Database: AGENTS_DEMO
-- Schema: PUBLIC
-- ============================================================================

USE DATABASE AGENTS_DEMO;
USE SCHEMA PUBLIC;

-- ============================================================================
-- 1. SF_CREATE_ACCOUNT
-- ============================================================================
-- Create a new Salesforce account
-- Input: VARCHAR (JSON string with account data, Name is required)
-- Output: VARCHAR (Account ID or JSON with error)
-- ============================================================================

CREATE OR REPLACE FUNCTION SF_CREATE_ACCOUNT(account_data VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
HANDLER = 'create_account_handler'
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py', '@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/accounts.py')
EXTERNAL_ACCESS_INTEGRATIONS = (SALESFORCE_API_INTEGRATION)
SECRETS = ('password' = SALESFORCE_PASSWORD, 'token' = SALESFORCE_TOKEN, 'username' = SALESFORCE_USERNAME)
AS
$$
import _snowflake
from accounts import AccountOperations
import json

def create_account_handler(account_data):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = AccountOperations(username, password, token)

        # Parse JSON string to dict
        if isinstance(account_data, str):
            account_data = json.loads(account_data)

        if isinstance(account_data, dict):
            name = account_data.get('Name')
            if not name:
                return json.dumps({'error': 'Name is required'})
            # Remove Name from kwargs
            kwargs = {k: v for k, v in account_data.items() if k != 'Name'}
            account_id = sf.create_account(name, **kwargs)
            # Return just the ID string
            return account_id
        else:
            return json.dumps({'error': 'Invalid account_data format'})
    except Exception as e:
        return json.dumps({'error': str(e)})
$$;

-- ============================================================================
-- 2. SF_UPDATE_ACCOUNT
-- ============================================================================
-- Update an existing Salesforce account
-- Input: account_id (VARCHAR), update_data (VARCHAR - JSON string)
-- Output: BOOLEAN (True if successful)
-- ============================================================================

CREATE OR REPLACE FUNCTION SF_UPDATE_ACCOUNT(account_id VARCHAR, update_data VARCHAR)
RETURNS BOOLEAN
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
HANDLER = 'update_account_handler'
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py', '@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/accounts.py')
EXTERNAL_ACCESS_INTEGRATIONS = (SALESFORCE_API_INTEGRATION)
SECRETS = ('password' = SALESFORCE_PASSWORD, 'token' = SALESFORCE_TOKEN, 'username' = SALESFORCE_USERNAME)
AS
$$
import _snowflake
from accounts import AccountOperations
import json

def update_account_handler(account_id, update_data):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = AccountOperations(username, password, token)

        # Parse JSON string to dict
        if isinstance(update_data, str):
            update_data = json.loads(update_data)

        return sf.update_account(account_id, update_data)
    except Exception as e:
        return False
$$;

-- ============================================================================
-- 3. SF_DELETE_ACCOUNT
-- ============================================================================
-- Delete a Salesforce account by ID
-- Input: account_id (VARCHAR)
-- Output: VARCHAR (success message or error JSON)
-- ============================================================================

CREATE OR REPLACE FUNCTION SF_DELETE_ACCOUNT(account_id VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
HANDLER = 'delete_account_handler'
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py', '@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/accounts.py')
EXTERNAL_ACCESS_INTEGRATIONS = (SALESFORCE_API_INTEGRATION)
SECRETS = ('password' = SALESFORCE_PASSWORD, 'token' = SALESFORCE_TOKEN, 'username' = SALESFORCE_USERNAME)
AS
$$
import _snowflake
from accounts import AccountOperations
import json

def delete_account_handler(account_id):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = AccountOperations(username, password, token)

        # Delete uses the core delete_record method
        result = sf.sf.Account.delete(account_id)

        return json.dumps({
            'success': True,
            'account_id': account_id,
            'message': 'Account deleted successfully'
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })
$$;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT '✅ Deployed 3 Account CRUD functions:' AS status;
SELECT '  - SF_CREATE_ACCOUNT(account_data VARCHAR)' AS function_1;
SELECT '  - SF_UPDATE_ACCOUNT(account_id VARCHAR, update_data VARCHAR)' AS function_2;
SELECT '  - SF_DELETE_ACCOUNT(account_id VARCHAR)' AS function_3;

-- Show all Salesforce functions
SHOW USER FUNCTIONS LIKE 'SF_%';
SHOW USER FUNCTIONS LIKE 'SALESFORCE_%';


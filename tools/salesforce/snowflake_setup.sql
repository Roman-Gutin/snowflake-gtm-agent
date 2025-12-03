-- ============================================================================
-- Salesforce Tools for Snowflake - UDF Setup
-- ============================================================================
-- This script creates Snowpark Python UDFs for Salesforce operations
-- Deploy with: snowsql -f snowflake_setup.sql
-- ============================================================================

-- ============================================================================
-- STEP 1: Create External Access Integration for Salesforce API
-- ============================================================================

-- Create network rule for Salesforce API access
CREATE OR REPLACE NETWORK RULE salesforce_api_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = (
    'login.salesforce.com:443',
    'test.salesforce.com:443',
    '*.salesforce.com:443',
    '*.force.com:443',
    '*.my.salesforce.com:443'
  );

-- Create secrets for Salesforce credentials
CREATE OR REPLACE SECRET salesforce_username
  TYPE = GENERIC_STRING
  SECRET_STRING = 'romangutin860@agentforce.com';

CREATE OR REPLACE SECRET salesforce_password
  TYPE = GENERIC_STRING
  SECRET_STRING = 'FuckSFDC1!';

CREATE OR REPLACE SECRET salesforce_token
  TYPE = GENERIC_STRING
  SECRET_STRING = 'iLARVeZyoXUeJm4a5aPwvBZ9';

-- Create external access integration
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION salesforce_api_integration
  ALLOWED_NETWORK_RULES = (salesforce_api_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (salesforce_username, salesforce_password, salesforce_token)
  ENABLED = TRUE;

-- ============================================================================
-- STEP 2: Create Stage for Python Files
-- ============================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE TEST;
USE SCHEMA PUBLIC;

CREATE OR REPLACE STAGE TEST.PUBLIC.SALESFORCE_STAGE
  COMMENT = 'Stage for Salesforce Python modules';

-- Upload Python files using Snow CLI (done via deployment script):
-- snow stage copy salesforce_tools/__init__.py @TEST.PUBLIC.SALESFORCE_STAGE/salesforce_tools/ --overwrite --auto-compress false
-- snow stage copy salesforce_tools/core.py @TEST.PUBLIC.SALESFORCE_STAGE/salesforce_tools/ --overwrite --auto-compress false
-- ... etc

-- Verify files are uploaded:
-- snow stage list @TEST.PUBLIC.SALESFORCE_STAGE/salesforce_tools/

-- ============================================================================
-- QUERY OPERATIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION salesforce_query_records(soql STRING)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5', 'requests')
IMPORTS = ('@TEST.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py')
HANDLER = 'query_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = (
    'username' = salesforce_username,
    'password' = salesforce_password,
    'token' = salesforce_token
)
AS
$$
import _snowflake
from core import SalesforceTools

def query_handler(soql):
    try:
        # Read credentials from Snowflake secrets
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')

        sf = SalesforceTools(username, password, token)
        results = sf.query_records(soql)
        return results
    except Exception as e:
        return {'error': str(e)}
$$;

-- ============================================================================
-- ACCOUNT OPERATIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION salesforce_get_account(account_id STRING)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@TEST.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py', '@TEST.PUBLIC.SALESFORCE_STAGE/salesforce_tools/accounts.py')
HANDLER = 'get_account_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = (
    'username' = salesforce_username,
    'password' = salesforce_password,
    'token' = salesforce_token
)
AS
$$
import _snowflake
from accounts import AccountOperations

def get_account_handler(account_id):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')

        sf = AccountOperations(username, password, token)
        return sf.get_account(account_id)
    except Exception as e:
        return {'error': str(e)}
$$;

CREATE OR REPLACE FUNCTION salesforce_create_account(account_data VARIANT)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/accounts.py')
HANDLER = 'create_account_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = (
    'username' = salesforce_username,
    'password' = salesforce_password,
    'token' = salesforce_token
)
AS
$$
import _snowflake
from accounts import AccountOperations

def create_account_handler(account_data):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')

        sf = AccountOperations(username, password, token)
        name = account_data.get('Name')
        if not name:
            return {'error': 'Name is required'}

        kwargs = {k: v for k, v in account_data.items() if k != 'Name'}
        account_id = sf.create_account(name, **kwargs)
        return account_id
    except Exception as e:
        return {'error': str(e)}
$$;

CREATE OR REPLACE FUNCTION salesforce_get_account_summary(account_id STRING)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/accounts.py')
HANDLER = 'get_account_summary_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = (
    'username' = salesforce_username,
    'password' = salesforce_password,
    'token' = salesforce_token
)
AS
$$
import _snowflake
from accounts import AccountOperations

def get_account_summary_handler(account_id):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')

        sf = AccountOperations(username, password, token)
        return sf.get_account_summary(account_id)
    except Exception as e:
        return {'error': str(e)}
$$;

-- ============================================================================
-- OPPORTUNITY OPERATIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION salesforce_get_opportunity(
    opportunity_id STRING,
    username STRING,
    password STRING,
    security_token STRING
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/opportunities.py')
HANDLER = 'get_opportunity_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('cred' = salesforce_credentials)
AS
$$
from opportunities import OpportunityOperations

def get_opportunity_handler(opportunity_id, username, password, security_token):
    try:
        sf = OpportunityOperations(username, password, security_token)
        return sf.get_opportunity(opportunity_id)
    except Exception as e:
        return {'error': str(e)}
$$;

CREATE OR REPLACE FUNCTION salesforce_create_opportunity(
    opportunity_data VARIANT,
    username STRING,
    password STRING,
    security_token STRING
)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/opportunities.py')
HANDLER = 'create_opportunity_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('cred' = salesforce_credentials)
AS
$$
from opportunities import OpportunityOperations

def create_opportunity_handler(opportunity_data, username, password, security_token):
    try:
        sf = OpportunityOperations(username, password, security_token)
        opportunity_id = sf.create_opportunity(opportunity_data)
        return opportunity_id
    except Exception as e:
        return {'error': str(e)}
$$;

CREATE OR REPLACE FUNCTION salesforce_update_opportunity(
    opportunity_id STRING,
    update_data VARIANT,
    username STRING,
    password STRING,
    security_token STRING
)
RETURNS BOOLEAN
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/opportunities.py')
HANDLER = 'update_opportunity_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('cred' = salesforce_credentials)
AS
$$
from opportunities import OpportunityOperations

def update_opportunity_handler(opportunity_id, update_data, username, password, security_token):
    try:
        sf = OpportunityOperations(username, password, security_token)
        return sf.update_opportunity(opportunity_id, update_data)
    except Exception as e:
        return False
$$;

CREATE OR REPLACE FUNCTION salesforce_get_pipeline_summary(
    username STRING,
    password STRING,
    security_token STRING
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/opportunities.py')
HANDLER = 'get_pipeline_summary_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('cred' = salesforce_credentials)
AS
$$
from opportunities import OpportunityOperations

def get_pipeline_summary_handler(username, password, security_token):
    try:
        sf = OpportunityOperations(username, password, security_token)
        return sf.get_pipeline_summary()
    except Exception as e:
        return {'error': str(e)}
$$;

-- ============================================================================
-- CONTACT OPERATIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION salesforce_get_contact(
    contact_id STRING,
    username STRING,
    password STRING,
    security_token STRING
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/contacts.py')
HANDLER = 'get_contact_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('cred' = salesforce_credentials)
AS
$$
from contacts import ContactOperations

def get_contact_handler(contact_id, username, password, security_token):
    try:
        sf = ContactOperations(username, password, security_token)
        return sf.get_contact(contact_id)
    except Exception as e:
        return {'error': str(e)}
$$;

-- ============================================================================
-- DISCOVERY OPERATIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION salesforce_list_objects(
    username STRING,
    password STRING,
    security_token STRING
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/discovery.py')
HANDLER = 'list_objects_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('cred' = salesforce_credentials)
AS
$$
from discovery import DiscoveryOperations

def list_objects_handler(username, password, security_token):
    try:
        sf = DiscoveryOperations(username, password, security_token)
        return sf.list_all_objects()
    except Exception as e:
        return {'error': str(e)}
$$;

CREATE OR REPLACE FUNCTION salesforce_get_object_summary(
    object_name STRING,
    username STRING,
    password STRING,
    security_token STRING
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@salesforce_packages/salesforce_tools/core.py', '@salesforce_packages/salesforce_tools/discovery.py')
HANDLER = 'get_object_summary_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('cred' = salesforce_credentials)
AS
$$
from discovery import DiscoveryOperations

def get_object_summary_handler(object_name, username, password, security_token):
    try:
        sf = DiscoveryOperations(username, password, security_token)
        return sf.get_object_summary(object_name)
    except Exception as e:
        return {'error': str(e)}
$$;

-- ============================================================================
-- RBAC: Grant Permissions
-- ============================================================================

-- Grant usage on external access integration to appropriate roles
GRANT USAGE ON INTEGRATION salesforce_api_integration TO ROLE ACCOUNTADMIN;
GRANT USAGE ON INTEGRATION salesforce_api_integration TO ROLE SYSADMIN;

-- Grant usage on schema
GRANT USAGE ON SCHEMA salesforce_tools TO ROLE PUBLIC;

-- Grant usage on all functions
GRANT USAGE ON ALL FUNCTIONS IN SCHEMA salesforce_tools TO ROLE PUBLIC;

-- Grant read on secret (if using secrets)
GRANT READ ON SECRET salesforce_credentials TO ROLE ACCOUNTADMIN;
GRANT READ ON SECRET salesforce_credentials TO ROLE SYSADMIN;

-- ============================================================================
-- Verification
-- ============================================================================

-- Show created objects
SHOW INTEGRATIONS LIKE 'salesforce_api_integration';
SHOW NETWORK RULES LIKE 'salesforce_api_network_rule';
SHOW SECRETS LIKE 'salesforce_credentials';
SHOW FUNCTIONS IN SCHEMA salesforce_tools;

SELECT 'Salesforce Tools deployed successfully!' AS status;
SELECT 'External Access Integration: salesforce_api_integration' AS integration;
SELECT 'Network Rule: salesforce_api_network_rule' AS network_rule;
SELECT 'Secret: salesforce_credentials' AS secret;
SELECT '11 UDFs created in salesforce_tools schema' AS functions;


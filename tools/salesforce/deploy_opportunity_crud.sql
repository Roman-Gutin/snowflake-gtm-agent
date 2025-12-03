-- ============================================================================
-- Salesforce Opportunity CRUD - Simple Deployment
-- ============================================================================
-- Deploy only the Opportunity CRUD functions that we know work locally
-- ============================================================================

USE DATABASE AGENTS_DEMO;
USE SCHEMA PUBLIC;

-- ============================================================================
-- Function 1: Query Opportunities
-- ============================================================================

CREATE OR REPLACE FUNCTION sf_query_opportunities(soql VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5', 'requests')
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py')
HANDLER = 'query_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('username' = salesforce_username, 'password' = salesforce_password, 'token' = salesforce_token)
AS
$$
import _snowflake
import json
from core import SalesforceTools

def query_handler(soql):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = SalesforceTools(username, password, token)
        results = sf.query_records(soql)
        return json.dumps(results)
    except Exception as e:
        return json.dumps({'error': str(e)})
$$;

-- ============================================================================
-- Function 2: Get Opportunity by ID
-- ============================================================================

CREATE OR REPLACE FUNCTION sf_get_opportunity(opportunity_id VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py', '@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/opportunities.py')
HANDLER = 'get_opportunity_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('username' = salesforce_username, 'password' = salesforce_password, 'token' = salesforce_token)
AS
$$
import _snowflake
import json
from opportunities import OpportunityOperations

def get_opportunity_handler(opportunity_id):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = OpportunityOperations(username, password, token)
        result = sf.get_opportunity(opportunity_id)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'error': str(e)})
$$;

-- ============================================================================
-- Function 3: Create Opportunity
-- ============================================================================

CREATE OR REPLACE FUNCTION SF_CREATE_OPPORTUNITY(OPPORTUNITY_DATA VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py', '@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/opportunities.py')
HANDLER = 'create_opportunity_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (SALESFORCE_API_INTEGRATION)
SECRETS = ('password' = SALESFORCE_PASSWORD, 'token' = SALESFORCE_TOKEN, 'username' = SALESFORCE_USERNAME)
AS
$$
import _snowflake
import json
from opportunities import OpportunityOperations

def create_opportunity_handler(opportunity_data):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = OpportunityOperations(username, password, token)

        # Parse JSON string to dict
        if isinstance(opportunity_data, str):
            opportunity_data = json.loads(opportunity_data)

        opp_id = sf.create_opportunity(opportunity_data)
        return json.dumps({'id': opp_id, 'success': True})
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})
$$;

-- ============================================================================
-- Function 4: Update Opportunity
-- ============================================================================

CREATE OR REPLACE FUNCTION SF_UPDATE_OPPORTUNITY(OPPORTUNITY_ID VARCHAR, UPDATE_DATA VARCHAR)
RETURNS BOOLEAN
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py', '@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/opportunities.py')
HANDLER = 'update_opportunity_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (SALESFORCE_API_INTEGRATION)
SECRETS = ('password' = SALESFORCE_PASSWORD, 'token' = SALESFORCE_TOKEN, 'username' = SALESFORCE_USERNAME)
AS
$$
import _snowflake
import json
from opportunities import OpportunityOperations

def update_opportunity_handler(opportunity_id, update_data):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = OpportunityOperations(username, password, token)

        # Parse JSON string to dict
        if isinstance(update_data, str):
            update_data = json.loads(update_data)

        return sf.update_opportunity(opportunity_id, update_data)
    except Exception as e:
        return False
$$;

-- ============================================================================
-- Function 5: Delete Opportunity
-- ============================================================================

CREATE OR REPLACE FUNCTION sf_delete_opportunity(opportunity_id VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('simple-salesforce==1.12.5')
IMPORTS = ('@AGENTS_DEMO.PUBLIC.SALESFORCE_STAGE/salesforce_tools/core.py')
HANDLER = 'delete_handler'
EXTERNAL_ACCESS_INTEGRATIONS = (salesforce_api_integration)
SECRETS = ('username' = salesforce_username, 'password' = salesforce_password, 'token' = salesforce_token)
AS
$$
import _snowflake
import json
from core import SalesforceTools

def delete_handler(opportunity_id):
    try:
        username = _snowflake.get_generic_secret_string('username')
        password = _snowflake.get_generic_secret_string('password')
        token = _snowflake.get_generic_secret_string('token')
        sf = SalesforceTools(username, password, token)
        success = sf.delete_record('Opportunity', opportunity_id)
        return json.dumps({'success': success})
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})
$$;

-- ============================================================================
-- Grant Permissions
-- ============================================================================

GRANT USAGE ON ALL FUNCTIONS IN SCHEMA AGENTS_DEMO.PUBLIC TO ROLE PUBLIC;

-- ============================================================================
-- Verification
-- ============================================================================

SHOW FUNCTIONS LIKE 'sf_%opportunity%' IN SCHEMA AGENTS_DEMO.PUBLIC;

SELECT 'Salesforce Opportunity CRUD functions deployed successfully!' AS status;


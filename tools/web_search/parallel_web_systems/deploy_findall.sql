-- ============================================================================
-- Parallel Web Systems FindAll API - Snowflake Deployment
-- ============================================================================
-- Deploy FindAll API UDFs to AGENTS_DEMO for entity discovery and enrichment
-- ============================================================================

USE ROLE SERVICE_ROLE;
USE DATABASE AGENTS_DEMO;
USE SCHEMA PUBLIC;
USE WAREHOUSE AGENTS_DEMO_WH;

-- ============================================================================
-- Step 1: Create Network Rule for Parallel API
-- ============================================================================

CREATE OR REPLACE NETWORK RULE PARALLEL_API_NETWORK_RULE
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('api.parallel.ai:443');

-- ============================================================================
-- Step 2: Create Secret for Parallel API Key
-- ============================================================================

CREATE OR REPLACE SECRET PARALLEL_API_KEY
    TYPE = GENERIC_STRING
    SECRET_STRING = 'JqIl5fheTM4tt8sLEuzkxFyRS1aAbBMUhnkwKBq0';

-- ============================================================================
-- Step 3: Create External Access Integration
-- ============================================================================

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION PARALLEL_API_INTEGRATION
    ALLOWED_NETWORK_RULES = (PARALLEL_API_NETWORK_RULE)
    ALLOWED_AUTHENTICATION_SECRETS = (PARALLEL_API_KEY)
    ENABLED = TRUE;

-- Grant usage to AGENTS_SERVICE_ROLE
GRANT USAGE ON INTEGRATION PARALLEL_API_INTEGRATION TO ROLE AGENTS_SERVICE_ROLE;

-- ============================================================================
-- Step 4: Create FindAll UDFs
-- ============================================================================

-- Switch to AGENTS_SERVICE_ROLE for UDF creation
USE ROLE AGENTS_SERVICE_ROLE;

-- 4a: Create FindAll Run
CREATE OR REPLACE FUNCTION CREATE_FINDALL_RUN(
    OBJECTIVE VARCHAR,
    ENTITY_TYPE VARCHAR,
    MATCH_CONDITIONS VARCHAR,
    GENERATOR VARCHAR DEFAULT 'core',
    MATCH_LIMIT INTEGER DEFAULT 10
)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('requests')
EXTERNAL_ACCESS_INTEGRATIONS = (PARALLEL_API_INTEGRATION)
SECRETS = ('api_key' = PARALLEL_API_KEY)
HANDLER = 'create_findall_handler'
COMMENT = 'Create a FindAll run to discover entities matching specified criteria'
AS
$$
import json
import requests
import _snowflake

BETA_HEADER = "findall-2025-09-15"
BASE_URL = "https://api.parallel.ai"

def create_findall_handler(objective, entity_type, match_conditions, generator, match_limit):
    try:
        api_key = _snowflake.get_generic_secret_string('api_key')
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "parallel-beta": BETA_HEADER
        }
        
        conditions = json.loads(match_conditions) if isinstance(match_conditions, str) else match_conditions
        
        payload = {
            "objective": objective,
            "entity_type": entity_type,
            "match_conditions": conditions,
            "generator": generator,
            "match_limit": match_limit
        }
        
        response = requests.post(f"{BASE_URL}/v1beta/findall/runs", headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                'success': True,
                'findall_id': result.get('findall_id'),
                'status': result.get('status', {}).get('status'),
                'is_active': result.get('status', {}).get('is_active'),
                'generator': result.get('generator'),
                'created_at': result.get('created_at')
            })
        else:
            return json.dumps({'success': False, 'error': f'HTTP {response.status_code}: {response.text}'})
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})
$$;

-- 4b: Get FindAll Status
CREATE OR REPLACE FUNCTION GET_FINDALL_STATUS(FINDALL_ID VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('requests')
EXTERNAL_ACCESS_INTEGRATIONS = (PARALLEL_API_INTEGRATION)
SECRETS = ('api_key' = PARALLEL_API_KEY)
HANDLER = 'get_status_handler'
COMMENT = 'Get the status and metrics of a FindAll run'
AS
$$
import json
import requests
import _snowflake

BETA_HEADER = "findall-2025-09-15"
BASE_URL = "https://api.parallel.ai"

def get_status_handler(findall_id):
    try:
        api_key = _snowflake.get_generic_secret_string('api_key')
        headers = {"x-api-key": api_key, "Content-Type": "application/json", "parallel-beta": BETA_HEADER}
        
        response = requests.get(f"{BASE_URL}/v1beta/findall/runs/{findall_id}", headers=headers, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            status_obj = result.get('status', {})
            return json.dumps({
                'success': True,
                'findall_id': findall_id,
                'status': status_obj.get('status'),
                'is_active': status_obj.get('is_active'),
                'metrics': status_obj.get('metrics', {}),
                'modified_at': result.get('modified_at')
            })
        else:
            return json.dumps({'success': False, 'error': f'HTTP {response.status_code}: {response.text}'})
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})
$$;

-- 4c: Get FindAll Results
CREATE OR REPLACE FUNCTION GET_FINDALL_RESULTS(FINDALL_ID VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('requests')
EXTERNAL_ACCESS_INTEGRATIONS = (PARALLEL_API_INTEGRATION)
SECRETS = ('api_key' = PARALLEL_API_KEY)
HANDLER = 'get_results_handler'
COMMENT = 'Get the matched candidates from a FindAll run'
AS
$$
import json
import requests
import _snowflake

BETA_HEADER = "findall-2025-09-15"
BASE_URL = "https://api.parallel.ai"

def get_results_handler(findall_id):
    try:
        api_key = _snowflake.get_generic_secret_string('api_key')
        headers = {"x-api-key": api_key, "Content-Type": "application/json", "parallel-beta": BETA_HEADER}

        response = requests.get(f"{BASE_URL}/v1beta/findall/runs/{findall_id}/result", headers=headers, timeout=120)

        if response.status_code == 200:
            result = response.json()
            run = result.get('run', {})
            candidates = result.get('candidates', [])
            matched = [c for c in candidates if c.get('match_status') == 'matched']

            return json.dumps({
                'success': True,
                'findall_id': findall_id,
                'status': run.get('status', {}).get('status'),
                'is_active': run.get('status', {}).get('is_active'),
                'total_candidates': len(candidates),
                'matched_count': len(matched),
                'candidates': matched
            })
        else:
            return json.dumps({'success': False, 'error': f'HTTP {response.status_code}: {response.text}'})
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})
$$;

-- 4d: Extend FindAll Run
CREATE OR REPLACE FUNCTION EXTEND_FINDALL(FINDALL_ID VARCHAR, ADDITIONAL_MATCH_LIMIT INTEGER)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('requests')
EXTERNAL_ACCESS_INTEGRATIONS = (PARALLEL_API_INTEGRATION)
SECRETS = ('api_key' = PARALLEL_API_KEY)
HANDLER = 'extend_handler'
COMMENT = 'Extend a FindAll run to find more matches'
AS
$$
import json
import requests
import _snowflake

BETA_HEADER = "findall-2025-09-15"
BASE_URL = "https://api.parallel.ai"

def extend_handler(findall_id, additional_match_limit):
    try:
        api_key = _snowflake.get_generic_secret_string('api_key')
        headers = {"x-api-key": api_key, "Content-Type": "application/json", "parallel-beta": BETA_HEADER}

        payload = {"additional_match_limit": additional_match_limit}
        response = requests.post(f"{BASE_URL}/v1beta/findall/runs/{findall_id}/extend", headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                'success': True,
                'findall_id': findall_id,
                'new_match_limit': result.get('match_limit'),
                'objective': result.get('objective')
            })
        else:
            return json.dumps({'success': False, 'error': f'HTTP {response.status_code}: {response.text}'})
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})
$$;

-- 4e: Enrich FindAll Run
CREATE OR REPLACE FUNCTION ENRICH_FINDALL(FINDALL_ID VARCHAR, OUTPUT_SCHEMA VARCHAR, PROCESSOR VARCHAR DEFAULT 'core')
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('requests')
EXTERNAL_ACCESS_INTEGRATIONS = (PARALLEL_API_INTEGRATION)
SECRETS = ('api_key' = PARALLEL_API_KEY)
HANDLER = 'enrich_handler'
COMMENT = 'Add enrichment to a FindAll run to gather additional data about matches'
AS
$$
import json
import requests
import _snowflake

BETA_HEADER = "findall-2025-09-15"
BASE_URL = "https://api.parallel.ai"

def enrich_handler(findall_id, output_schema, processor):
    try:
        api_key = _snowflake.get_generic_secret_string('api_key')
        headers = {"x-api-key": api_key, "Content-Type": "application/json", "parallel-beta": BETA_HEADER}

        schema = json.loads(output_schema) if isinstance(output_schema, str) else output_schema
        payload = {"processor": processor, "output_schema": schema}
        response = requests.post(f"{BASE_URL}/v1beta/findall/runs/{findall_id}/enrich", headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                'success': True,
                'findall_id': findall_id,
                'enrichments': result.get('enrichments', []),
                'objective': result.get('objective')
            })
        else:
            return json.dumps({'success': False, 'error': f'HTTP {response.status_code}: {response.text}'})
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})
$$;

-- 4f: Cancel FindAll Run
CREATE OR REPLACE FUNCTION CANCEL_FINDALL(FINDALL_ID VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('requests')
EXTERNAL_ACCESS_INTEGRATIONS = (PARALLEL_API_INTEGRATION)
SECRETS = ('api_key' = PARALLEL_API_KEY)
HANDLER = 'cancel_handler'
COMMENT = 'Cancel a running FindAll run'
AS
$$
import json
import requests
import _snowflake

BETA_HEADER = "findall-2025-09-15"
BASE_URL = "https://api.parallel.ai"

def cancel_handler(findall_id):
    try:
        api_key = _snowflake.get_generic_secret_string('api_key')
        headers = {"x-api-key": api_key, "Content-Type": "application/json", "parallel-beta": BETA_HEADER}

        response = requests.post(f"{BASE_URL}/v1beta/findall/runs/{findall_id}/cancel", headers=headers, timeout=120)

        if response.status_code == 200:
            result = response.json()
            return json.dumps({
                'success': True,
                'findall_id': findall_id,
                'status': result.get('status', {}).get('status'),
                'message': 'FindAll run cancelled'
            })
        else:
            return json.dumps({'success': False, 'error': f'HTTP {response.status_code}: {response.text}'})
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})
$$;

-- ============================================================================
-- Step 5: Create FINDALL_RUNS Tracking Table (Optional)
-- ============================================================================

CREATE TABLE IF NOT EXISTS FINDALL_RUNS (
    FINDALL_ID VARCHAR(100) PRIMARY KEY,
    OBJECTIVE VARCHAR(2000),
    ENTITY_TYPE VARCHAR(100),
    MATCH_CONDITIONS VARIANT,
    GENERATOR VARCHAR(50),
    MATCH_LIMIT INTEGER,
    STATUS VARCHAR(50),
    IS_ACTIVE BOOLEAN,
    MATCHED_COUNT INTEGER,
    RESULTS VARIANT,
    ENRICHMENTS VARIANT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER()
);

-- ============================================================================
-- Step 6: Create MANAGE_FINDALL_RUN Procedure (Optional)
-- ============================================================================

CREATE OR REPLACE PROCEDURE MANAGE_FINDALL_RUN(ACTION VARCHAR, FINDALL_ID VARCHAR, PAYLOAD VARCHAR)
RETURNS VARIANT
LANGUAGE JAVASCRIPT
EXECUTE AS CALLER
AS
$$
var payload = JSON.parse(PAYLOAD || '{}');
var result = {};
var stmt, rs, binds;

if (ACTION === 'log') {
    binds = [FINDALL_ID, payload.objective, payload.entity_type, JSON.stringify(payload.match_conditions), payload.generator, payload.match_limit];
    stmt = snowflake.createStatement({
        sqlText: "INSERT INTO FINDALL_RUNS (FINDALL_ID, OBJECTIVE, ENTITY_TYPE, MATCH_CONDITIONS, GENERATOR, MATCH_LIMIT, STATUS, IS_ACTIVE) SELECT ?, ?, ?, PARSE_JSON(?), ?, ?, 'created', TRUE",
        binds: binds
    });
    stmt.execute();
    result = {success: true, action: 'logged', findall_id: FINDALL_ID};
}
else if (ACTION === 'update_status') {
    binds = [payload.status, payload.is_active, payload.matched_count, FINDALL_ID];
    stmt = snowflake.createStatement({
        sqlText: "UPDATE FINDALL_RUNS SET STATUS = ?, IS_ACTIVE = ?, MATCHED_COUNT = ?, UPDATED_AT = CURRENT_TIMESTAMP() WHERE FINDALL_ID = ?",
        binds: binds
    });
    stmt.execute();
    result = {success: true, action: 'status_updated', findall_id: FINDALL_ID};
}
else if (ACTION === 'get_recent') {
    var limit = payload.limit || 10;
    stmt = snowflake.createStatement({
        sqlText: "SELECT FINDALL_ID, OBJECTIVE, ENTITY_TYPE, STATUS, MATCHED_COUNT, CREATED_AT FROM FINDALL_RUNS ORDER BY CREATED_AT DESC LIMIT " + limit
    });
    rs = stmt.execute();
    var runs = [];
    while (rs.next()) {
        runs.push({
            findall_id: rs.getColumnValue('FINDALL_ID'),
            objective: rs.getColumnValue('OBJECTIVE'),
            status: rs.getColumnValue('STATUS'),
            matched_count: rs.getColumnValue('MATCHED_COUNT')
        });
    }
    result = {success: true, runs: runs};
}
else {
    result = {success: false, error: 'Unknown action: ' + ACTION};
}
return result;
$$;

-- ============================================================================
-- Step 7: Verify Deployment
-- ============================================================================

SHOW FUNCTIONS LIKE '%FINDALL%' IN SCHEMA AGENTS_DEMO.PUBLIC;


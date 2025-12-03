-- ============================================================================
-- GTME Snowflake Infrastructure Setup
-- ============================================================================
-- Run this ONCE as ACCOUNTADMIN before deploying any tools.
-- This creates the base infrastructure: database, warehouse, roles, and grants.
-- ============================================================================

USE ROLE ACCOUNTADMIN;

-- ============================================================================
-- Step 1: Create Database and Warehouse
-- ============================================================================

CREATE DATABASE IF NOT EXISTS AGENTS_DEMO
    COMMENT = 'Database for GTME Cortex AI Agent tools';

CREATE WAREHOUSE IF NOT EXISTS AGENTS_DEMO_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for GTME agent operations';

-- ============================================================================
-- Step 2: Create Roles (RBAC)
-- ============================================================================

-- Service role: owns integrations, secrets, UDFs
CREATE ROLE IF NOT EXISTS AGENTS_SERVICE_ROLE
    COMMENT = 'Role for managing agent tools and integrations';

-- User role: can execute UDFs but not modify
CREATE ROLE IF NOT EXISTS AGENT_SERVICE_USER
    COMMENT = 'Role for users who run the agent';

-- ============================================================================
-- Step 3: Role Hierarchy
-- ============================================================================

-- ACCOUNTADMIN -> AGENTS_SERVICE_ROLE -> AGENT_SERVICE_USER
GRANT ROLE AGENTS_SERVICE_ROLE TO ROLE ACCOUNTADMIN;
GRANT ROLE AGENT_SERVICE_USER TO ROLE AGENTS_SERVICE_ROLE;

-- ============================================================================
-- Step 4: Database and Warehouse Grants
-- ============================================================================

-- Service role gets full control
GRANT ALL ON DATABASE AGENTS_DEMO TO ROLE AGENTS_SERVICE_ROLE;
GRANT ALL ON WAREHOUSE AGENTS_DEMO_WH TO ROLE AGENTS_SERVICE_ROLE;
GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE AGENTS_SERVICE_ROLE;

-- User role gets usage
GRANT USAGE ON DATABASE AGENTS_DEMO TO ROLE AGENT_SERVICE_USER;
GRANT USAGE ON WAREHOUSE AGENTS_DEMO_WH TO ROLE AGENT_SERVICE_USER;

-- ============================================================================
-- Step 5: Schema Setup
-- ============================================================================

USE DATABASE AGENTS_DEMO;

CREATE SCHEMA IF NOT EXISTS PUBLIC;

GRANT ALL ON SCHEMA PUBLIC TO ROLE AGENTS_SERVICE_ROLE;
GRANT USAGE ON SCHEMA PUBLIC TO ROLE AGENT_SERVICE_USER;

-- Future grants so new UDFs are automatically accessible
GRANT USAGE ON FUTURE FUNCTIONS IN SCHEMA PUBLIC TO ROLE AGENT_SERVICE_USER;
GRANT USAGE ON FUTURE PROCEDURES IN SCHEMA PUBLIC TO ROLE AGENT_SERVICE_USER;

-- ============================================================================
-- Step 6: Verify Setup
-- ============================================================================

SHOW DATABASES LIKE 'AGENTS_DEMO';
SHOW WAREHOUSES LIKE 'AGENTS_DEMO_WH';
SHOW ROLES LIKE 'AGENTS%';

SELECT 'GTME Infrastructure setup complete!' AS status;
SELECT 'Next: Deploy integrations from tools/*/deploy_*.sql' AS next_step;


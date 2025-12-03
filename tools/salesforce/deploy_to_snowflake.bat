@echo off
REM ========================================
REM Deploy Salesforce Tools to Snowflake
REM ========================================

setlocal enabledelayedexpansion

echo =========================================
echo Salesforce Tools - Snowflake Deployment
echo =========================================
echo.

REM Configuration
set SNOWFLAKE_DATABASE=TEST
set SNOWFLAKE_SCHEMA=PUBLIC
set SNOWFLAKE_ROLE=ACCOUNTADMIN
set STAGE_NAME=SALESFORCE_STAGE

REM Check if Snow CLI is installed
where snow >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Snow CLI not found. Please install it first:
    echo    pip install snowflake-cli-labs
    exit /b 1
)

echo ✅ Snow CLI found
echo.

REM Check if required files exist
echo Checking required files...
set "files=salesforce_tools\__init__.py salesforce_tools\core.py salesforce_tools\accounts.py salesforce_tools\opportunities.py salesforce_tools\contacts.py salesforce_tools\discovery.py snowflake_setup.sql"

for %%f in (%files%) do (
    if not exist "%%f" (
        echo ❌ Required file not found: %%f
        exit /b 1
    )
    echo   ✓ %%f
)

echo.
echo =========================================
echo Step 1: Upload Python Files to Stage
echo =========================================
echo.

REM Upload Python files using Snow CLI
echo Uploading salesforce_tools\__init__.py...
snow stage copy salesforce_tools\__init__.py "@%SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%.%STAGE_NAME%/salesforce_tools/" --overwrite --auto-compress false

echo Uploading salesforce_tools\core.py...
snow stage copy salesforce_tools\core.py "@%SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%.%STAGE_NAME%/salesforce_tools/" --overwrite --auto-compress false

echo Uploading salesforce_tools\accounts.py...
snow stage copy salesforce_tools\accounts.py "@%SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%.%STAGE_NAME%/salesforce_tools/" --overwrite --auto-compress false

echo Uploading salesforce_tools\opportunities.py...
snow stage copy salesforce_tools\opportunities.py "@%SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%.%STAGE_NAME%/salesforce_tools/" --overwrite --auto-compress false

echo Uploading salesforce_tools\contacts.py...
snow stage copy salesforce_tools\contacts.py "@%SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%.%STAGE_NAME%/salesforce_tools/" --overwrite --auto-compress false

echo Uploading salesforce_tools\discovery.py...
snow stage copy salesforce_tools\discovery.py "@%SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%.%STAGE_NAME%/salesforce_tools/" --overwrite --auto-compress false

echo.
echo ✅ Python files uploaded successfully
echo.

REM Verify files are uploaded
echo Verifying uploaded files...
snow stage list "@%SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%.%STAGE_NAME%/salesforce_tools/"

echo.
echo =========================================
echo Step 2: Execute Setup SQL Script
echo =========================================
echo.

REM Execute the setup script
echo Running snowflake_setup.sql...
snow sql -f snowflake_setup.sql

echo.
echo ✅ Setup script executed successfully
echo.

echo =========================================
echo Step 3: Verify Installation
echo =========================================
echo.

REM Verify functions are created
echo Checking created functions...
snow sql -q "SHOW FUNCTIONS LIKE '%%salesforce%%' IN SCHEMA %SNOWFLAKE_DATABASE%.%SNOWFLAKE_SCHEMA%;"

echo.
echo =========================================
echo Deployment Complete! 🎉
echo =========================================
echo.
echo Next steps:
echo 1. Run tests: snow sql -f test_sfdc_tools.sql
echo 2. Try querying accounts:
echo    snow sql -q "SELECT salesforce_query_records('SELECT Id, Name FROM Account LIMIT 5');"
echo.
echo See README.md for detailed usage instructions.
echo.

pause


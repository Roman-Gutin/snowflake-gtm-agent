"""
Salesforce Tools

Reusable tool definitions for Salesforce CRUD operations.
"""

ALL_TOOLS = [
    {
        "tool_spec": {
            "type": "generic",
            "name": "SALESFORCE_QUERY_RECORDS",
            "description": "Query any Salesforce object using SOQL. Use this to list accounts, opportunities, contacts, or any records.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "SOQL": {"type": "string", "description": "SOQL query. Examples: 'SELECT Id, Name FROM Account LIMIT 100'"}
                },
                "required": ["SOQL"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SALESFORCE_GET_ACCOUNT",
            "description": "Get a single Salesforce account by ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ACCOUNT_ID": {"type": "string", "description": "Salesforce account ID (e.g., '001...')"}
                },
                "required": ["ACCOUNT_ID"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SF_CREATE_ACCOUNT",
            "description": "Create a new Salesforce account. Returns the new account ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ACCOUNT_DATA": {"type": "string", "description": "JSON string with account fields. Required: Name. Example: '{\"Name\": \"Acme Corp\", \"Industry\": \"Technology\"}'"}
                },
                "required": ["ACCOUNT_DATA"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SF_UPDATE_ACCOUNT",
            "description": "Update an existing Salesforce account.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ACCOUNT_ID": {"type": "string", "description": "Salesforce account ID"},
                    "UPDATE_DATA": {"type": "string", "description": "JSON string with fields to update"}
                },
                "required": ["ACCOUNT_ID", "UPDATE_DATA"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SF_DELETE_ACCOUNT",
            "description": "Delete a Salesforce account by ID. Use with caution.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ACCOUNT_ID": {"type": "string", "description": "Salesforce account ID to delete"}
                },
                "required": ["ACCOUNT_ID"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SF_GET_OPPORTUNITY",
            "description": "Get a single Salesforce opportunity by ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "OPPORTUNITY_ID": {"type": "string", "description": "Salesforce opportunity ID (e.g., '006...')"}
                },
                "required": ["OPPORTUNITY_ID"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SF_CREATE_OPPORTUNITY",
            "description": "Create a new Salesforce opportunity. Returns the new opportunity ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "OPPORTUNITY_DATA": {"type": "string", "description": "JSON string. Required: Name, AccountId, StageName, CloseDate. Example: '{\"Name\": \"Big Deal\", \"AccountId\": \"001xxx\", \"StageName\": \"Prospecting\", \"CloseDate\": \"2025-12-31\"}'"}
                },
                "required": ["OPPORTUNITY_DATA"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SF_UPDATE_OPPORTUNITY",
            "description": "Update an existing Salesforce opportunity.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "OPPORTUNITY_ID": {"type": "string", "description": "Salesforce opportunity ID"},
                    "UPDATE_DATA": {"type": "string", "description": "JSON string with fields to update"}
                },
                "required": ["OPPORTUNITY_ID", "UPDATE_DATA"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "SF_DELETE_OPPORTUNITY",
            "description": "Delete a Salesforce opportunity by ID. Use with caution.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "OPPORTUNITY_ID": {"type": "string", "description": "Salesforce opportunity ID to delete"}
                },
                "required": ["OPPORTUNITY_ID"]
            }
        }
    }
]


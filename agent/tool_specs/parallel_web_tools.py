"""
Parallel Web Systems Tools

Tool definitions for Parallel Web Systems FindAll API - entity discovery and enrichment.
Includes tracking tools to log runs to FINDALL_RUNS hybrid table.
"""

ALL_TOOLS = [
    {
        "tool_spec": {
            "type": "generic",
            "name": "CREATE_FINDALL_RUN",
            "description": "Create a FindAll run to discover entities (companies, people, etc.) matching specified criteria. Returns a findall_id to track the async operation. IMPORTANT: After calling this, you MUST call MANAGE_FINDALL_RUN with action='log' to record the run in the tracking table. Use GET_FINDALL_STATUS to check progress and GET_FINDALL_RESULTS to retrieve matches.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "OBJECTIVE": {
                        "type": "string",
                        "description": "Natural language description of what entities to find (e.g., 'Find AI companies that raised Series A in 2024')"
                    },
                    "ENTITY_TYPE": {
                        "type": "string",
                        "description": "Type of entity to find (e.g., 'companies', 'people', 'organizations')"
                    },
                    "MATCH_CONDITIONS": {
                        "type": "string",
                        "description": "JSON array of conditions each entity must match. Format: '[{\"name\": \"condition_id\", \"description\": \"condition description\"}]'"
                    },
                    "GENERATOR": {
                        "type": "string",
                        "description": "Generator to use: 'base', 'core' (default), 'pro', or 'preview'"
                    },
                    "MATCH_LIMIT": {
                        "type": "integer",
                        "description": "Maximum number of matches to find (5-1000). Default: 10"
                    }
                },
                "required": ["OBJECTIVE", "ENTITY_TYPE", "MATCH_CONDITIONS"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "MANAGE_FINDALL_RUN",
            "description": "Manage FindAll run tracking in the FINDALL_RUNS hybrid table. Use this to log runs, update status, save results/enrichments, or query historical runs. Actions: 'log' (after CREATE_FINDALL_RUN), 'update_status', 'save_results', 'save_enrichments', 'get_details', 'get_recent'.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ACTION": {
                        "type": "string",
                        "description": "Action to perform: 'log' (log new run), 'update_status' (update status/matched_count), 'save_results' (save matched entities), 'save_enrichments' (save enrichment data), 'get_details' (get full run details), 'get_recent' (list recent runs)"
                    },
                    "FINDALL_ID": {
                        "type": "string",
                        "description": "The FindAll run ID. Required for all actions except 'get_recent'."
                    },
                    "PAYLOAD": {
                        "type": "string",
                        "description": "JSON payload with action-specific data. For 'log': {objective, entity_type, match_conditions, generator, match_limit}. For 'update_status': {status, is_active, matched_count}. For 'save_results': {results}. For 'save_enrichments': {enrichments}. For 'get_recent': {limit}."
                    }
                },
                "required": ["ACTION", "FINDALL_ID", "PAYLOAD"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "GET_FINDALL_STATUS",
            "description": "Check the status and progress metrics of a FindAll run. Returns is_active (true if still running) and metrics about matches found.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "FINDALL_ID": {
                        "type": "string",
                        "description": "The FindAll run ID returned by CREATE_FINDALL_RUN"
                    }
                },
                "required": ["FINDALL_ID"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "GET_FINDALL_RESULTS",
            "description": "Get the matched entities from a completed FindAll run. Returns array of candidates with their entity details and match status.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "FINDALL_ID": {
                        "type": "string",
                        "description": "The FindAll run ID returned by CREATE_FINDALL_RUN"
                    }
                },
                "required": ["FINDALL_ID"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "EXTEND_FINDALL",
            "description": "Extend a FindAll run to find additional matches beyond the original limit.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "FINDALL_ID": {
                        "type": "string",
                        "description": "The FindAll run ID to extend"
                    },
                    "ADDITIONAL_MATCH_LIMIT": {
                        "type": "integer",
                        "description": "Number of additional matches to find"
                    }
                },
                "required": ["FINDALL_ID", "ADDITIONAL_MATCH_LIMIT"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "ENRICH_FINDALL",
            "description": "Add enrichment to a FindAll run to gather additional structured data about matched entities. Define output schema to specify what data to extract.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "FINDALL_ID": {
                        "type": "string",
                        "description": "The FindAll run ID to enrich"
                    },
                    "OUTPUT_SCHEMA": {
                        "type": "string",
                        "description": "JSON schema defining what data to extract (e.g., '{\"type\":\"object\",\"properties\":{\"revenue\":{\"type\":\"string\"},\"employees\":{\"type\":\"integer\"}}}')"
                    },
                    "PROCESSOR": {
                        "type": "string",
                        "description": "Processor to use: 'base', 'core' (default), or 'pro'"
                    }
                },
                "required": ["FINDALL_ID", "OUTPUT_SCHEMA"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "CANCEL_FINDALL",
            "description": "Cancel a running FindAll run. Use if no longer needed or taking too long.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "FINDALL_ID": {
                        "type": "string",
                        "description": "The FindAll run ID to cancel"
                    }
                },
                "required": ["FINDALL_ID"]
            }
        }
    }
]


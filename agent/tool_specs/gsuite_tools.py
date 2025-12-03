"""
Google Workspace Tools

Reusable tool definitions for Google Docs, Sheets, and Drive.
"""

# Google Docs tools
docs_tools = [
    {
        "tool_spec": {
            "type": "generic",
            "name": "create_google_doc",
            "description": "Create a new Google Doc with a title. Returns the document ID and web link.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the new document"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "read_google_doc",
            "description": "Read a Google Document",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "The Google Doc ID"},
                    "include_content": {"type": "boolean", "description": "TRUE: Extracts and parses content into sections. FALSE: Returns minimal metadata"}
                },
                "required": ["document_id", "include_content"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "insert_text_google_doc",
            "description": "Insert text at a specific position in a Google Doc. Position 1 is the start.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "The Google Doc ID"},
                    "text": {"type": "string", "description": "Text to insert"},
                    "index_pos": {"type": "integer", "description": "Position to insert at (1 = start)"}
                },
                "required": ["document_id", "text", "index_pos"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "delete_content_google_doc",
            "description": "Delete content from a Google Doc between start and end positions.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "The Google Doc ID"},
                    "start_index": {"type": "integer", "description": "Start position"},
                    "end_index": {"type": "integer", "description": "End position"}
                },
                "required": ["document_id", "start_index", "end_index"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "replace_all_text_google_doc",
            "description": "Find and replace all occurrences of text in a Google Doc.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "The Google Doc ID"},
                    "find_text": {"type": "string", "description": "Text to find"},
                    "replace_text": {"type": "string", "description": "Text to replace with"}
                },
                "required": ["document_id", "find_text", "replace_text"]
            }
        }
    }
]

# Google Sheets tools
sheets_tools = [
    {
        "tool_spec": {
            "type": "generic",
            "name": "create_google_sheet",
            "description": "Create a new Google Sheet with a title. Returns spreadsheet ID and web link.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the new spreadsheet"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "read_sheet_data",
            "description": "Read data from a Google Sheet range (e.g., 'Sheet1!A1:D10').",
            "input_schema": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "The Google Sheet ID"},
                    "range_notation": {"type": "string", "description": "Range in A1 notation"}
                },
                "required": ["spreadsheet_id", "range_notation"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "write_sheet_data",
            "description": "Write data to a Google Sheet range. Data as JSON 2D array string.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "The Google Sheet ID"},
                    "range_notation": {"type": "string", "description": "Range in A1 notation"},
                    "data_values": {"type": "string", "description": "JSON 2D array: '[[\"Name\", \"Age\"], [\"Alice\", 30]]'"}
                },
                "required": ["spreadsheet_id", "range_notation", "data_values"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "append_sheet_data",
            "description": "Append rows to the end of a Google Sheet.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "The Google Sheet ID"},
                    "range_notation": {"type": "string", "description": "Range to append to"},
                    "data_values": {"type": "string", "description": "JSON 2D array of rows to append"}
                },
                "required": ["spreadsheet_id", "range_notation", "data_values"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "update_cell",
            "description": "Update a single cell in a Google Sheet.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "The Google Sheet ID"},
                    "cell_notation": {"type": "string", "description": "Cell reference (e.g., 'Sheet1!A1')"},
                    "value": {"type": "string", "description": "New cell value"}
                },
                "required": ["spreadsheet_id", "cell_notation", "value"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "clear_sheet_data",
            "description": "Clear data from a Google Sheet range without deleting cells.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "The Google Sheet ID"},
                    "range_notation": {"type": "string", "description": "Range to clear"}
                },
                "required": ["spreadsheet_id", "range_notation"]
            }
        }
    }
]

# Google Drive tools
drive_tools = [
    {
        "tool_spec": {
            "type": "generic",
            "name": "create_drive_folder",
            "description": "Create a new folder in Google Drive. Returns folder ID and web link.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the new folder"},
                    "parent_id": {"type": "string", "description": "Parent folder ID (optional)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "list_folder_contents",
            "description": "List all files and folders within a Google Drive folder.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "The folder ID to list"},
                    "page_size": {"type": "integer", "description": "Max items to return (1-1000)"},
                    "order_by": {"type": "string", "description": "Sort order (e.g., 'name', 'modifiedTime desc')"}
                },
                "required": ["folder_id"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "get_folder_metadata",
            "description": "Get metadata for a Google Drive folder including permissions.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "The folder ID"}
                },
                "required": ["folder_id"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "update_drive_folder",
            "description": "Update folder properties (name, description, color).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "The folder ID"},
                    "name": {"type": "string", "description": "New name (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "folder_color_rgb": {"type": "string", "description": "Color in hex (optional)"}
                },
                "required": ["folder_id"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "delete_drive_file",
            "description": "Delete a file or folder from Google Drive (moves to trash).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file or folder ID to delete"}
                },
                "required": ["file_id"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "share_drive_folder",
            "description": "Share a folder with a user by email.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "The folder ID"},
                    "email": {"type": "string", "description": "Email to share with"},
                    "role": {"type": "string", "description": "Permission: reader, writer, commenter"},
                    "send_notification": {"type": "boolean", "description": "Send email notification"}
                },
                "required": ["folder_id", "email"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "share_drive_file",
            "description": "Share a file with a user by email.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file ID"},
                    "email": {"type": "string", "description": "Email to share with"},
                    "role": {"type": "string", "description": "Permission: reader, writer, commenter"},
                    "send_notification": {"type": "boolean", "description": "Send email notification"}
                },
                "required": ["file_id", "email"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "get_file_metadata",
            "description": "Get metadata for a Google Drive file.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file ID"}
                },
                "required": ["file_id"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "rename_drive_file",
            "description": "Rename a file or folder in Google Drive.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file or folder ID"},
                    "new_name": {"type": "string", "description": "New name"}
                },
                "required": ["file_id", "new_name"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "create_drive_file",
            "description": "Create a new file in Google Drive.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "File name"},
                    "mime_type": {"type": "string", "description": "MIME type (default: text/plain)"},
                    "parent_id": {"type": "string", "description": "Parent folder ID (optional)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "tool_spec": {
            "type": "generic",
            "name": "update_file_content",
            "description": "Update the content of a file in Google Drive.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file ID"},
                    "content": {"type": "string", "description": "New file content"},
                    "mime_type": {"type": "string", "description": "MIME type (default: text/plain)"}
                },
                "required": ["file_id", "content"]
            }
        }
    }
]

# All GSuite tools combined
ALL_TOOLS = docs_tools + sheets_tools + drive_tools

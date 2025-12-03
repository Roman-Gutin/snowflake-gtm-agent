"""
Google Workspace Tools for Snowflake Integration

This package provides comprehensive Google Docs API integration for Snowflake UDFs.
All methods are designed to work as Snowflake User Defined Functions (UDFs) with
OAuth2 authentication via _snowflake.get_oauth_access_token('cred').

Author: Snowflake Integration Team
Version: 1.0.0
"""

from .gdocs_handler import GDocsHandler

__version__ = "1.0.0"
__all__ = ["GDocsHandler"]


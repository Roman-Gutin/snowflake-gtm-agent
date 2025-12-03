"""
Salesforce Tools for Snowflake
Production-ready Salesforce integration for Snowflake UDFs
"""

# For local testing, use relative imports
# For Snowflake, the modules are imported directly
try:
    from .core import SalesforceTools
    from .accounts import AccountOperations
    from .opportunities import OpportunityOperations
    from .contacts import ContactOperations
    from .discovery import DiscoveryOperations
except ImportError:
    # Fallback for Snowflake environment
    from core import SalesforceTools
    from accounts import AccountOperations
    from opportunities import OpportunityOperations
    from contacts import ContactOperations
    from discovery import DiscoveryOperations

__version__ = "1.0.0"
__all__ = [
    "SalesforceTools",
    "AccountOperations",
    "OpportunityOperations",
    "ContactOperations",
    "DiscoveryOperations",
]


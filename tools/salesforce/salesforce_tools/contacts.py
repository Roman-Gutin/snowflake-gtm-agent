"""
Contact-specific operations
"""

from typing import Dict, List, Any, Optional
try:
    from .core import SalesforceTools
except ImportError:
    from core import SalesforceTools


class ContactOperations(SalesforceTools):
    """Contact-specific helper functions"""
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get contact by ID
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Contact record
        """
        return self.get_record('Contact', contact_id)
    
    def create_contact(self, data: Dict[str, Any]) -> str:
        """
        Create a new contact
        
        Args:
            data: Contact data (must include LastName)
            
        Returns:
            Created contact ID
            
        Example:
            create_contact({
                'FirstName': 'John',
                'LastName': 'Doe',
                'Email': 'john.doe@example.com',
                'AccountId': '001xxx'
            })
        """
        if 'LastName' not in data:
            raise ValueError("LastName is required")
        
        return self.create_record('Contact', data)
    
    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a contact
        
        Args:
            contact_id: Contact ID
            data: Fields to update
            
        Returns:
            True if successful
        """
        return self.update_record('Contact', contact_id, data)
    
    def search_contacts(self, name: str) -> List[Dict[str, Any]]:
        """
        Search contacts by name
        
        Args:
            name: Name to search for
            
        Returns:
            List of matching contacts
        """
        soql = f"""
            SELECT Id, Name, Email, Phone, AccountId, Account.Name
            FROM Contact
            WHERE Name LIKE '%{name}%'
        """
        return self.query_records(soql)
    
    def get_all_contacts(self, fields: Optional[List[str]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all contacts
        
        Args:
            fields: List of fields to retrieve
            limit: Maximum number of records
            
        Returns:
            List of contacts
        """
        if fields is None:
            fields = ['Id', 'Name', 'Email', 'Phone', 'Title', 'AccountId']
        
        fields_str = ', '.join(fields)
        soql = f"SELECT {fields_str} FROM Contact LIMIT {limit}"
        return self.query_records(soql)
    
    def get_contacts_by_account(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all contacts for an account
        
        Args:
            account_id: Account ID
            
        Returns:
            List of contacts
        """
        soql = f"""
            SELECT Id, Name, Title, Email, Phone
            FROM Contact
            WHERE AccountId = '{account_id}'
            ORDER BY Name
        """
        return self.query_records(soql)
    
    def search_contacts_by_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Search contacts by email
        
        Args:
            email: Email to search for
            
        Returns:
            List of matching contacts
        """
        soql = f"""
            SELECT Id, Name, Email, Phone, AccountId, Account.Name
            FROM Contact
            WHERE Email LIKE '%{email}%'
        """
        return self.query_records(soql)


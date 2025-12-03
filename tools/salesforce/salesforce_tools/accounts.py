"""
Account-specific operations
"""

from typing import Dict, List, Any, Optional
try:
    from .core import SalesforceTools
except ImportError:
    from core import SalesforceTools


class AccountOperations(SalesforceTools):
    """Account-specific helper functions"""
    
    def get_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get account by ID
        
        Args:
            account_id: Account ID
            
        Returns:
            Account record
        """
        return self.get_record('Account', account_id)
    
    def create_account(self, name: str, **kwargs) -> str:
        """
        Create a new account
        
        Args:
            name: Account name (required)
            **kwargs: Additional fields (Type, Industry, Website, Phone, etc.)
            
        Returns:
            Created account ID
            
        Example:
            create_account('Acme Corp', Type='Customer', Industry='Technology')
        """
        data = {'Name': name, **kwargs}
        return self.create_record('Account', data)
    
    def update_account(self, account_id: str, data: Dict[str, Any]) -> bool:
        """
        Update an account
        
        Args:
            account_id: Account ID
            data: Fields to update
            
        Returns:
            True if successful
        """
        return self.update_record('Account', account_id, data)
    
    def search_accounts(self, name: str) -> List[Dict[str, Any]]:
        """
        Search accounts by name
        
        Args:
            name: Account name to search for
            
        Returns:
            List of matching accounts
        """
        return self.search_records('Account', 'Name', name)
    
    def get_all_accounts(self, fields: Optional[List[str]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all accounts
        
        Args:
            fields: List of fields to retrieve (default: Id, Name, Type, Industry)
            limit: Maximum number of records (default: 100)
            
        Returns:
            List of accounts
        """
        if fields is None:
            fields = ['Id', 'Name', 'Type', 'Industry', 'BillingCity', 'BillingState']
        
        fields_str = ', '.join(fields)
        soql = f"SELECT {fields_str} FROM Account LIMIT {limit}"
        return self.query_records(soql)
    
    def get_account_opportunities(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all opportunities for an account
        
        Args:
            account_id: Account ID
            
        Returns:
            List of opportunities
        """
        soql = f"""
            SELECT Id, Name, StageName, Amount, CloseDate, Probability
            FROM Opportunity
            WHERE AccountId = '{account_id}'
            ORDER BY CloseDate DESC
        """
        return self.query_records(soql)
    
    def get_account_contacts(self, account_id: str) -> List[Dict[str, Any]]:
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
    
    def get_account_summary(self, account_id: str) -> Dict[str, Any]:
        """
        Get complete account summary with related records
        
        Args:
            account_id: Account ID
            
        Returns:
            Dictionary with account, opportunities, and contacts
        """
        account = self.get_account(account_id)
        opportunities = self.get_account_opportunities(account_id)
        contacts = self.get_account_contacts(account_id)
        
        # Calculate opportunity totals
        total_opp_value = sum(opp.get('Amount', 0) or 0 for opp in opportunities)
        open_opps = [opp for opp in opportunities if not opp.get('IsClosed', False)]
        
        return {
            'account': account,
            'opportunities': {
                'total': len(opportunities),
                'open': len(open_opps),
                'total_value': total_opp_value,
                'records': opportunities
            },
            'contacts': {
                'total': len(contacts),
                'records': contacts
            }
        }


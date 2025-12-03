"""
Opportunity-specific operations
"""

from typing import Dict, List, Any, Optional
try:
    from .core import SalesforceTools
except ImportError:
    from core import SalesforceTools


class OpportunityOperations(SalesforceTools):
    """Opportunity-specific helper functions"""
    
    def get_opportunity(self, opportunity_id: str) -> Dict[str, Any]:
        """
        Get opportunity by ID
        
        Args:
            opportunity_id: Opportunity ID
            
        Returns:
            Opportunity record
        """
        return self.get_record('Opportunity', opportunity_id)
    
    def create_opportunity(self, data: Dict[str, Any]) -> str:
        """
        Create a new opportunity
        
        Args:
            data: Opportunity data (must include Name, AccountId, StageName, CloseDate)
            
        Returns:
            Created opportunity ID
            
        Example:
            create_opportunity({
                'Name': 'Q4 2025 Deal',
                'AccountId': '001xxx',
                'Amount': 250000,
                'CloseDate': '2025-12-31',
                'StageName': 'Prospecting'
            })
        """
        # Validate required fields
        required = ['Name', 'AccountId', 'StageName', 'CloseDate']
        missing = [f for f in required if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        
        return self.create_record('Opportunity', data)
    
    def update_opportunity(self, opportunity_id: str, data: Dict[str, Any]) -> bool:
        """
        Update an opportunity
        
        Args:
            opportunity_id: Opportunity ID
            data: Fields to update
            
        Returns:
            True if successful
        """
        return self.update_record('Opportunity', opportunity_id, data)
    
    def search_opportunities(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search opportunities by name
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching opportunities
        """
        return self.search_records('Opportunity', 'Name', keyword)
    
    def get_all_opportunities(self, fields: Optional[List[str]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all opportunities
        
        Args:
            fields: List of fields to retrieve
            limit: Maximum number of records
            
        Returns:
            List of opportunities
        """
        if fields is None:
            fields = ['Id', 'Name', 'AccountId', 'Amount', 'StageName', 'CloseDate', 'Probability']
        
        fields_str = ', '.join(fields)
        soql = f"SELECT {fields_str} FROM Opportunity ORDER BY CloseDate DESC LIMIT {limit}"
        return self.query_records(soql)
    
    def get_open_opportunities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all open (not closed) opportunities
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of open opportunities
        """
        soql = f"""
            SELECT Id, Name, AccountId, Account.Name, Amount, StageName, CloseDate, Probability
            FROM Opportunity
            WHERE IsClosed = false
            ORDER BY CloseDate ASC
            LIMIT {limit}
        """
        return self.query_records(soql)
    
    def get_opportunities_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """
        Get opportunities by stage
        
        Args:
            stage: Stage name (e.g., 'Prospecting', 'Qualification', 'Closed Won')
            
        Returns:
            List of opportunities in that stage
        """
        soql = f"""
            SELECT Id, Name, AccountId, Account.Name, Amount, CloseDate
            FROM Opportunity
            WHERE StageName = '{stage}'
            ORDER BY CloseDate ASC
        """
        return self.query_records(soql)
    
    def get_opportunities_by_account(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all opportunities for an account
        
        Args:
            account_id: Account ID
            
        Returns:
            List of opportunities
        """
        soql = f"""
            SELECT Id, Name, Amount, StageName, CloseDate, Probability
            FROM Opportunity
            WHERE AccountId = '{account_id}'
            ORDER BY CloseDate DESC
        """
        return self.query_records(soql)
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """
        Get pipeline summary with totals by stage
        
        Returns:
            Dictionary with pipeline metrics
        """
        # Get all open opportunities
        opps = self.get_open_opportunities(limit=1000)
        
        # Calculate totals
        total_value = sum(opp.get('Amount', 0) or 0 for opp in opps)
        weighted_value = sum((opp.get('Amount', 0) or 0) * (opp.get('Probability', 0) or 0) / 100 for opp in opps)
        
        # Group by stage
        by_stage = {}
        for opp in opps:
            stage = opp.get('StageName', 'Unknown')
            if stage not in by_stage:
                by_stage[stage] = {'count': 0, 'value': 0}
            by_stage[stage]['count'] += 1
            by_stage[stage]['value'] += opp.get('Amount', 0) or 0
        
        return {
            'total_opportunities': len(opps),
            'total_value': total_value,
            'weighted_value': weighted_value,
            'by_stage': by_stage
        }
    
    def close_opportunity(self, opportunity_id: str, won: bool, close_date: Optional[str] = None) -> bool:
        """
        Close an opportunity as won or lost
        
        Args:
            opportunity_id: Opportunity ID
            won: True for Closed Won, False for Closed Lost
            close_date: Close date (YYYY-MM-DD), defaults to today
            
        Returns:
            True if successful
        """
        from datetime import date
        
        stage = 'Closed Won' if won else 'Closed Lost'
        data = {
            'StageName': stage,
            'CloseDate': close_date or date.today().isoformat()
        }
        
        return self.update_opportunity(opportunity_id, data)


"""
Core Salesforce operations using simple-salesforce
Only includes reliable, production-ready functions
"""

from typing import Dict, List, Any, Optional
from simple_salesforce import Salesforce
import json


class SalesforceTools:
    """
    Core Salesforce operations for Snowflake UDFs
    
    Focuses on data operations (CRUD) which work reliably via API.
    Schema operations (creating fields/objects) should be done via Salesforce UI.
    """
    
    def __init__(self, username: str, password: str, security_token: str):
        """
        Initialize Salesforce connection
        
        Args:
            username: Salesforce username
            password: Salesforce password
            security_token: Salesforce security token
        """
        self.sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token
        )
        self.instance_url = f"https://{self.sf.sf_instance}"
    
    # ========================================
    # QUERY OPERATIONS
    # ========================================
    
    def query_records(self, soql: str) -> List[Dict[str, Any]]:
        """
        Execute SOQL query and return results
        
        Args:
            soql: SOQL query string
            
        Returns:
            List of records as dictionaries
            
        Example:
            query_records("SELECT Id, Name FROM Account LIMIT 10")
        """
        try:
            result = self.sf.query(soql)
            return result['records']
        except Exception as e:
            raise Exception(f"Query failed: {str(e)}")
    
    def query_all_records(self, soql: str) -> List[Dict[str, Any]]:
        """
        Execute SOQL query and return ALL results (handles pagination)
        
        Args:
            soql: SOQL query string
            
        Returns:
            List of all records
        """
        try:
            result = self.sf.query_all(soql)
            return result['records']
        except Exception as e:
            raise Exception(f"Query all failed: {str(e)}")
    
    def get_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """
        Get a single record by ID
        
        Args:
            object_name: Salesforce object name (e.g., 'Account')
            record_id: Record ID
            
        Returns:
            Record as dictionary
        """
        try:
            obj = getattr(self.sf, object_name)
            return obj.get(record_id)
        except Exception as e:
            raise Exception(f"Get record failed: {str(e)}")
    
    # ========================================
    # CREATE OPERATIONS
    # ========================================
    
    def create_record(self, object_name: str, data: Dict[str, Any]) -> str:
        """
        Create a new record
        
        Args:
            object_name: Salesforce object name
            data: Record data as dictionary
            
        Returns:
            Created record ID
            
        Example:
            create_record('Account', {'Name': 'Acme Corp', 'Industry': 'Technology'})
        """
        try:
            obj = getattr(self.sf, object_name)
            result = obj.create(data)
            
            if result.get('success'):
                return result['id']
            else:
                raise Exception(f"Create failed: {result.get('errors', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Create record failed: {str(e)}")
    
    # ========================================
    # UPDATE OPERATIONS
    # ========================================
    
    def update_record(self, object_name: str, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Update an existing record
        
        Args:
            object_name: Salesforce object name
            record_id: Record ID to update
            data: Updated fields as dictionary
            
        Returns:
            True if successful
            
        Example:
            update_record('Account', '001xxx', {'Industry': 'Retail'})
        """
        try:
            obj = getattr(self.sf, object_name)
            result = obj.update(record_id, data)
            return result == 204  # Salesforce returns 204 on successful update
        except Exception as e:
            raise Exception(f"Update record failed: {str(e)}")
    
    # ========================================
    # DELETE OPERATIONS
    # ========================================
    
    def delete_record(self, object_name: str, record_id: str) -> bool:
        """
        Delete a record
        
        Args:
            object_name: Salesforce object name
            record_id: Record ID to delete
            
        Returns:
            True if successful
        """
        try:
            obj = getattr(self.sf, object_name)
            result = obj.delete(record_id)
            return result == 204  # Salesforce returns 204 on successful delete
        except Exception as e:
            raise Exception(f"Delete record failed: {str(e)}")
    
    # ========================================
    # SEARCH OPERATIONS
    # ========================================
    
    def search_records(self, object_name: str, field: str, value: str) -> List[Dict[str, Any]]:
        """
        Search records by field value
        
        Args:
            object_name: Salesforce object name
            field: Field name to search
            value: Value to search for
            
        Returns:
            List of matching records
            
        Example:
            search_records('Account', 'Name', 'Acme')
        """
        soql = f"SELECT Id, Name FROM {object_name} WHERE {field} LIKE '%{value}%'"
        return self.query_records(soql)
    
    # ========================================
    # DISCOVERY OPERATIONS
    # ========================================
    
    def describe_object(self, object_name: str) -> Dict[str, Any]:
        """
        Get object metadata
        
        Args:
            object_name: Salesforce object name
            
        Returns:
            Object metadata including fields
        """
        try:
            obj = getattr(self.sf, object_name)
            return obj.describe()
        except Exception as e:
            raise Exception(f"Describe object failed: {str(e)}")
    
    def list_objects(self) -> List[str]:
        """
        List all objects in the org
        
        Returns:
            List of object names
        """
        try:
            describe = self.sf.describe()
            return [obj['name'] for obj in describe['sobjects']]
        except Exception as e:
            raise Exception(f"List objects failed: {str(e)}")
    
    def list_custom_objects(self) -> List[str]:
        """
        List only custom objects
        
        Returns:
            List of custom object names
        """
        try:
            describe = self.sf.describe()
            return [obj['name'] for obj in describe['sobjects'] if obj['custom']]
        except Exception as e:
            raise Exception(f"List custom objects failed: {str(e)}")
    
    def get_field_names(self, object_name: str) -> List[str]:
        """
        Get all field names for an object
        
        Args:
            object_name: Salesforce object name
            
        Returns:
            List of field names
        """
        try:
            describe = self.describe_object(object_name)
            return [field['name'] for field in describe['fields']]
        except Exception as e:
            raise Exception(f"Get field names failed: {str(e)}")
    
    # ========================================
    # UTILITY FUNCTIONS
    # ========================================
    
    def count_records(self, object_name: str, where_clause: str = "") -> int:
        """
        Count records in an object
        
        Args:
            object_name: Salesforce object name
            where_clause: Optional WHERE clause (without 'WHERE')
            
        Returns:
            Number of records
            
        Example:
            count_records('Account', "Industry = 'Technology'")
        """
        where = f" WHERE {where_clause}" if where_clause else ""
        soql = f"SELECT COUNT() FROM {object_name}{where}"
        
        try:
            result = self.sf.query(soql)
            return result['totalSize']
        except Exception as e:
            raise Exception(f"Count records failed: {str(e)}")
    
    def get_record_url(self, record_id: str) -> str:
        """
        Get Salesforce UI URL for a record
        
        Args:
            record_id: Record ID
            
        Returns:
            Full URL to record in Salesforce UI
        """
        return f"{self.instance_url}/lightning/r/{record_id}/view"


"""
Discovery and metadata operations
"""

from typing import Dict, List, Any
try:
    from .core import SalesforceTools
except ImportError:
    from core import SalesforceTools


class DiscoveryOperations(SalesforceTools):
    """Discovery and metadata helper functions"""
    
    def get_org_info(self) -> Dict[str, Any]:
        """
        Get organization information
        
        Returns:
            Dictionary with org details
        """
        describe = self.sf.describe()
        
        all_objects = describe['sobjects']
        custom_objects = [obj for obj in all_objects if obj['custom']]
        standard_objects = [obj for obj in all_objects if not obj['custom']]
        
        return {
            'instance_url': self.instance_url,
            'total_objects': len(all_objects),
            'custom_objects': len(custom_objects),
            'standard_objects': len(standard_objects),
            'encoding': describe.get('encoding'),
            'max_batch_size': describe.get('maxBatchSize')
        }
    
    def list_all_objects(self) -> List[Dict[str, str]]:
        """
        List all objects with basic info
        
        Returns:
            List of objects with name, label, and type
        """
        describe = self.sf.describe()
        
        return [
            {
                'name': obj['name'],
                'label': obj['label'],
                'custom': obj['custom'],
                'queryable': obj['queryable'],
                'createable': obj['createable']
            }
            for obj in describe['sobjects']
        ]
    
    def list_custom_objects_detailed(self) -> List[Dict[str, Any]]:
        """
        List custom objects with detailed information
        
        Returns:
            List of custom objects with metadata
        """
        describe = self.sf.describe()
        
        custom_objects = []
        for obj in describe['sobjects']:
            if obj['custom']:
                custom_objects.append({
                    'name': obj['name'],
                    'label': obj['label'],
                    'label_plural': obj['labelPlural'],
                    'queryable': obj['queryable'],
                    'createable': obj['createable'],
                    'updateable': obj['updateable'],
                    'deletable': obj['deletable']
                })
        
        return custom_objects
    
    def get_object_fields(self, object_name: str) -> List[Dict[str, Any]]:
        """
        Get all fields for an object with details
        
        Args:
            object_name: Salesforce object name
            
        Returns:
            List of fields with metadata
        """
        describe = self.describe_object(object_name)
        
        return [
            {
                'name': field['name'],
                'label': field['label'],
                'type': field['type'],
                'custom': field.get('custom', False),
                'required': not field.get('nillable', True),
                'unique': field.get('unique', False),
                'length': field.get('length'),
                'precision': field.get('precision'),
                'scale': field.get('scale')
            }
            for field in describe['fields']
        ]
    
    def get_custom_fields(self, object_name: str) -> List[Dict[str, Any]]:
        """
        Get only custom fields for an object
        
        Args:
            object_name: Salesforce object name
            
        Returns:
            List of custom fields
        """
        all_fields = self.get_object_fields(object_name)
        return [field for field in all_fields if field['custom']]
    
    def get_picklist_values(self, object_name: str, field_name: str) -> List[str]:
        """
        Get picklist values for a field
        
        Args:
            object_name: Salesforce object name
            field_name: Picklist field name
            
        Returns:
            List of picklist values
        """
        describe = self.describe_object(object_name)
        
        for field in describe['fields']:
            if field['name'] == field_name:
                if field['type'] == 'picklist' and field.get('picklistValues'):
                    return [v['value'] for v in field['picklistValues'] if v['active']]
        
        return []
    
    def search_objects_by_keyword(self, keyword: str) -> List[Dict[str, str]]:
        """
        Search for objects by keyword in name or label
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching objects
        """
        describe = self.sf.describe()
        keyword_lower = keyword.lower()
        
        matching = []
        for obj in describe['sobjects']:
            if (keyword_lower in obj['name'].lower() or 
                keyword_lower in obj['label'].lower()):
                matching.append({
                    'name': obj['name'],
                    'label': obj['label'],
                    'custom': obj['custom']
                })
        
        return matching
    
    def get_object_record_count(self, object_name: str) -> int:
        """
        Get total record count for an object
        
        Args:
            object_name: Salesforce object name
            
        Returns:
            Number of records
        """
        return self.count_records(object_name)
    
    def get_object_summary(self, object_name: str) -> Dict[str, Any]:
        """
        Get complete summary of an object
        
        Args:
            object_name: Salesforce object name
            
        Returns:
            Dictionary with object metadata and statistics
        """
        describe = self.describe_object(object_name)
        fields = self.get_object_fields(object_name)
        custom_fields = [f for f in fields if f['custom']]
        record_count = self.get_object_record_count(object_name)
        
        return {
            'name': describe['name'],
            'label': describe['label'],
            'label_plural': describe['labelPlural'],
            'custom': describe['custom'],
            'queryable': describe['queryable'],
            'createable': describe['createable'],
            'updateable': describe['updateable'],
            'deletable': describe['deletable'],
            'total_fields': len(fields),
            'custom_fields': len(custom_fields),
            'record_count': record_count,
            'fields': fields
        }


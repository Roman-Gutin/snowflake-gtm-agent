"""
Google Sheets Handler for Snowflake UDFs

This module provides a comprehensive handler class for Google Sheets API operations.
All methods are designed to work as Snowflake UDFs with Service Account authentication.

Author: Snowflake Integration Team
Version: 2.0.0
"""

import json
import requests
try:
    from auth_helper_oauth import OAuthHelper
except ImportError:
    from auth_helper import ServiceAccountAuth as OAuthHelper


class GSheetsHandler:
    """
    Handler class for Google Sheets API operations in Snowflake UDFs.

    All methods use Service Account authentication via auth_helper.py
    and return structured JSON responses with success/error handling.
    """

    BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
    TIMEOUT = 60  # seconds

    def __init__(self, snowflake_module=None):
        """
        Initialize the handler.

        Args:
            snowflake_module: The _snowflake module (injected in Snowflake UDF context)
        """
        self._snowflake = snowflake_module
        self._auth = OAuthHelper(snowflake_module) if snowflake_module else None

    def _get_access_token(self):
        """Get access token from Service Account."""
        if self._auth is None:
            raise Exception("Snowflake module not initialized")
        return self._auth.get_access_token()
    
    def _make_request(self, method, url, data=None, operation_name='API_CALL'):
        """
        Make HTTP request to Google Sheets API with error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Full URL to call
            data: Request body (for POST/PUT)
            operation_name: Name of operation for error messages
            
        Returns:
            dict: Response data or error dict
        """
        try:
            token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=self.TIMEOUT)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=self.TIMEOUT)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.TIMEOUT)
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}', 'operation': operation_name}
            
            if response.status_code >= 400:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'operation': operation_name
                }
            
            return response.json() if response.text else {}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation_name}
    
    # ========================================
    # SPREADSHEET OPERATIONS
    # ========================================
    
    def create_spreadsheet(self, title="Untitled Spreadsheet"):
        """
        Create a new Google Sheet.
        
        Args:
            title: Title of the new spreadsheet
            
        Returns:
            dict: {'success': bool, 'spreadsheetId': str, 'spreadsheetUrl': str}
        """
        try:
            url = self.BASE_URL
            data = {
                'properties': {
                    'title': title
                }
            }
            
            result = self._make_request('POST', url, data, 'CREATE_SPREADSHEET')
            
            if 'spreadsheetId' in result:
                return {
                    'success': True,
                    'operation': 'CREATE_SPREADSHEET',
                    'spreadsheetId': result['spreadsheetId'],
                    'title': result['properties']['title'],
                    'spreadsheetUrl': result.get('spreadsheetUrl', f"https://docs.google.com/spreadsheets/d/{result['spreadsheetId']}/edit")
                }
            else:
                return result
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CREATE_SPREADSHEET'}
    
    def read_sheet_data(self, spreadsheet_id, range_notation):
        """
        Read data from a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_notation: A1 notation (e.g., 'Sheet1!A1:C10')
            
        Returns:
            dict: {'success': bool, 'values': list, 'range': str}
        """
        try:
            url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_notation}"
            result = self._make_request('GET', url, operation_name='READ_SHEET_DATA')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'READ_SHEET_DATA',
                'range': result.get('range', range_notation),
                'values': result.get('values', []),
                'row_count': len(result.get('values', []))
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'READ_SHEET_DATA'}
    
    def write_sheet_data(self, spreadsheet_id, range_notation, values):
        """
        Write data to a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_notation: A1 notation (e.g., 'Sheet1!A1')
            values: 2D array of values [[row1], [row2], ...]
            
        Returns:
            dict: {'success': bool, 'updatedCells': int, 'updatedRange': str}
        """
        try:
            url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_notation}?valueInputOption=USER_ENTERED"
            data = {
                'range': range_notation,
                'values': values
            }
            
            result = self._make_request('PUT', url, data, 'WRITE_SHEET_DATA')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'WRITE_SHEET_DATA',
                'updatedRange': result.get('updatedRange', range_notation),
                'updatedRows': result.get('updatedRows', 0),
                'updatedColumns': result.get('updatedColumns', 0),
                'updatedCells': result.get('updatedCells', 0)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'WRITE_SHEET_DATA'}
    
    def append_sheet_data(self, spreadsheet_id, range_notation, values):
        """
        Append data to a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_notation: A1 notation for the range (e.g., 'Sheet1' or 'Sheet1!A:C')
            values: 2D array of values to append
            
        Returns:
            dict: {'success': bool, 'updates': dict}
        """
        try:
            url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_notation}:append?valueInputOption=USER_ENTERED"
            data = {
                'range': range_notation,
                'values': values
            }
            
            result = self._make_request('POST', url, data, 'APPEND_SHEET_DATA')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            updates = result.get('updates', {})
            return {
                'success': True,
                'operation': 'APPEND_SHEET_DATA',
                'updatedRange': updates.get('updatedRange', ''),
                'updatedRows': updates.get('updatedRows', 0),
                'updatedColumns': updates.get('updatedColumns', 0),
                'updatedCells': updates.get('updatedCells', 0)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'APPEND_SHEET_DATA'}
    
    def update_cell(self, spreadsheet_id, cell_notation, value):
        """
        Update a single cell.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            cell_notation: A1 notation for single cell (e.g., 'Sheet1!B2')
            value: Value to set
            
        Returns:
            dict: {'success': bool, 'updatedCell': str}
        """
        try:
            return self.write_sheet_data(spreadsheet_id, cell_notation, [[value]])
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'UPDATE_CELL'}
    
    def clear_sheet_data(self, spreadsheet_id, range_notation):
        """
        Clear data from a range.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_notation: A1 notation (e.g., 'Sheet1!A1:C10')
            
        Returns:
            dict: {'success': bool, 'clearedRange': str}
        """
        try:
            url = f"{self.BASE_URL}/{spreadsheet_id}/values/{range_notation}:clear"
            result = self._make_request('POST', url, {}, 'CLEAR_SHEET_DATA')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'CLEAR_SHEET_DATA',
                'clearedRange': result.get('clearedRange', range_notation)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CLEAR_SHEET_DATA'}


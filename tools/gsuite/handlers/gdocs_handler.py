"""
Google Docs Handler for Snowflake UDFs

This module provides a comprehensive handler class for Google Docs API operations.
All methods are designed to work as Snowflake UDFs with Service Account authentication.

Supported Operations:
- Document Reading (get document content, structure, metadata)
- Document Creation (create new documents)
- Text Operations (insert, delete, replace text)
- Formatting (text style, paragraph style)
- Lists (create/delete bullets, numbered lists)
- Tables (insert, modify, delete tables and cells)
- Images (insert, replace, delete images)
- Page Breaks (insert page breaks)
- Named Ranges (create, delete named ranges)
- Headers/Footers (create, delete headers and footers)
- Sections (insert section breaks, update section styles)
- Comments (future enhancement)

API Reference: https://developers.google.com/workspace/docs/api/reference/rest/v1/documents
"""

import json
import requests
try:
    from auth_helper_oauth import OAuthHelper
except ImportError:
    from auth_helper import ServiceAccountAuth as OAuthHelper


class GDocsHandler:
    """
    Handler class for Google Docs API operations in Snowflake UDFs.

    All methods use OAuth authentication via auth_helper_oauth.py
    and return structured JSON responses with success/error handling.
    """

    BASE_URL = "https://docs.googleapis.com/v1/documents"
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
            raise RuntimeError("Snowflake module not initialized. This class must be used within a Snowflake UDF.")
        return self._auth.get_access_token()
    
    def _make_request(self, method, url, data=None, operation_name="API_CALL"):
        """
        Make an HTTP request to Google Docs API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to call
            data: Request body (for POST requests)
            operation_name: Name of the operation for error reporting
            
        Returns:
            dict: Response data or error dict
        """
        try:
            access_token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=self.TIMEOUT)
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}', 'operation': operation_name}
            
            if response.status_code not in [200, 201]:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'operation': operation_name
                }
            
            return response.json()
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation_name}
    
    # ========================================
    # DOCUMENT OPERATIONS
    # ========================================
    
    def create_document(self, title="Untitled Document"):
        """
        Create a new Google Doc.
        
        Args:
            title: Title of the new document
            
        Returns:
            dict: {
                'success': bool,
                'operation': 'CREATE_DOC',
                'document_id': str,
                'title': str,
                'document_url': str
            }
        """
        try:
            url = self.BASE_URL
            data = {'title': title}
            
            result = self._make_request('POST', url, data, 'CREATE_DOC')
            
            if 'documentId' in result:
                return {
                    'success': True,
                    'operation': 'CREATE_DOC',
                    'document_id': result['documentId'],
                    'title': result.get('title', title),
                    'document_url': f"https://docs.google.com/document/d/{result['documentId']}/edit"
                }
            else:
                return result
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CREATE_DOC'}
    
    def read_document(self, document_id, extract_sections=True):
        """
        Read a Google Doc and extract its content.
        
        Args:
            document_id: The ID of the document to read
            extract_sections: Whether to parse content into sections by headings
            
        Returns:
            dict: {
                'success': bool,
                'operation': 'READ_DOC',
                'document_id': str,
                'title': str,
                'full_content': str,
                'content_length': int,
                'sections': list (if extract_sections=True),
                'sections_count': int,
                'document_url': str
            }
        """
        try:
            url = f"{self.BASE_URL}/{document_id}"
            result = self._make_request('GET', url, operation_name='READ_DOC')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            doc_data = result
            
            # Extract text content
            full_content = []
            sections = []
            current_section = None
            
            if 'body' in doc_data and 'content' in doc_data['body']:
                for element in doc_data['body']['content']:
                    if 'paragraph' in element:
                        para = element['paragraph']
                        para_text = []
                        
                        # Check if this is a heading
                        is_heading = False
                        heading_level = None
                        if 'paragraphStyle' in para:
                            style_type = para['paragraphStyle'].get('namedStyleType', '')
                            if style_type.startswith('HEADING_'):
                                is_heading = True
                                heading_level = style_type
                        
                        # Extract text from paragraph elements
                        if 'elements' in para:
                            for elem in para['elements']:
                                if 'textRun' in elem:
                                    text = elem['textRun'].get('content', '')
                                    para_text.append(text)
                        
                        para_content = ''.join(para_text)
                        full_content.append(para_content)
                        
                        # Handle sections if requested
                        if extract_sections:
                            if is_heading:
                                # Save previous section
                                if current_section is not None:
                                    sections.append(current_section)
                                # Start new section
                                current_section = {
                                    'title': para_content.strip(),
                                    'level': heading_level,
                                    'content': ''
                                }
                            elif current_section is not None:
                                current_section['content'] += para_content
                            else:
                                # Content before first heading
                                if not sections:
                                    sections.append({
                                        'title': 'Introduction',
                                        'level': 'NORMAL_TEXT',
                                        'content': para_content
                                    })
                
                # Add last section
                if extract_sections and current_section is not None:
                    sections.append(current_section)
            
            full_text = ''.join(full_content)
            
            return {
                'success': True,
                'operation': 'READ_DOC',
                'document_id': document_id,
                'title': doc_data.get('title', 'Untitled'),
                'full_content': full_text,
                'content_length': len(full_text),
                'sections': sections if extract_sections else [],
                'sections_count': len(sections) if extract_sections else 0,
                'document_url': f"https://docs.google.com/document/d/{document_id}/edit"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'READ_DOC'}
    
    # ========================================
    # TEXT OPERATIONS
    # ========================================
    
    def insert_text(self, document_id, text, index=1):
        """
        Insert text at a specific index in the document.
        
        Args:
            document_id: The ID of the document
            text: Text to insert
            index: Character index where to insert (1 = start of document body)
            
        Returns:
            dict: {'success': bool, 'operation': 'INSERT_TEXT', 'text_length': int}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'insertText': {
                            'location': {'index': index},
                            'text': text
                        }
                    }
                ]
            }
            
            result = self._make_request('POST', url, data, 'INSERT_TEXT')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'INSERT_TEXT',
                'text_length': len(text),
                'document_id': document_id
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'INSERT_TEXT'}

    def delete_content(self, document_id, start_index, end_index):
        """
        Delete content from a document.

        Args:
            document_id: The ID of the document
            start_index: Start index of content to delete
            end_index: End index of content to delete

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_CONTENT', 'deleted_length': int}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'deleteContentRange': {
                            'range': {
                                'startIndex': start_index,
                                'endIndex': end_index
                            }
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_CONTENT')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_CONTENT',
                'deleted_length': end_index - start_index,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_CONTENT'}

    def replace_all_text(self, document_id, find_text, replace_text, match_case=False):
        """
        Replace all occurrences of text in a document.

        Args:
            document_id: The ID of the document
            find_text: Text to find
            replace_text: Text to replace with
            match_case: Whether to match case

        Returns:
            dict: {'success': bool, 'operation': 'REPLACE_TEXT', 'occurrences_changed': int}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'replaceAllText': {
                            'containsText': {
                                'text': find_text,
                                'matchCase': match_case
                            },
                            'replaceText': replace_text
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'REPLACE_TEXT')

            if 'error' in result and not result.get('success', True):
                return result

            occurrences = 0
            if 'replies' in result and len(result['replies']) > 0:
                if 'replaceAllText' in result['replies'][0]:
                    occurrences = result['replies'][0]['replaceAllText'].get('occurrencesChanged', 0)

            return {
                'success': True,
                'operation': 'REPLACE_TEXT',
                'occurrences_changed': occurrences,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'REPLACE_TEXT'}

    # ========================================
    # FORMATTING OPERATIONS
    # ========================================

    def update_text_style(self, document_id, start_index, end_index, bold=None, italic=None,
                          underline=None, font_size=None, foreground_color=None):
        """
        Update text style for a range of text.

        Args:
            document_id: The ID of the document
            start_index: Start index of text to style
            end_index: End index of text to style
            bold: True/False to set bold
            italic: True/False to set italic
            underline: True/False to set underline
            font_size: Font size in points
            foreground_color: RGB color dict {'red': 0-1, 'green': 0-1, 'blue': 0-1}

        Returns:
            dict: {'success': bool, 'operation': 'UPDATE_TEXT_STYLE'}
        """
        try:
            text_style = {}
            fields = []

            if bold is not None:
                text_style['bold'] = bold
                fields.append('bold')
            if italic is not None:
                text_style['italic'] = italic
                fields.append('italic')
            if underline is not None:
                text_style['underline'] = underline
                fields.append('underline')
            if font_size is not None:
                text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}
                fields.append('fontSize')
            if foreground_color is not None:
                text_style['foregroundColor'] = {'color': {'rgbColor': foreground_color}}
                fields.append('foregroundColor')

            if not fields:
                return {'success': False, 'error': 'No style properties specified', 'operation': 'UPDATE_TEXT_STYLE'}

            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'updateTextStyle': {
                            'range': {
                                'startIndex': start_index,
                                'endIndex': end_index
                            },
                            'textStyle': text_style,
                            'fields': ','.join(fields)
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'UPDATE_TEXT_STYLE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'UPDATE_TEXT_STYLE',
                'styled_length': end_index - start_index,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'UPDATE_TEXT_STYLE'}

    def update_paragraph_style(self, document_id, start_index, end_index,
                               named_style_type=None, alignment=None,
                               line_spacing=None, space_above=None, space_below=None):
        """
        Update paragraph style for a range.

        Args:
            document_id: The ID of the document
            start_index: Start index of paragraph range
            end_index: End index of paragraph range
            named_style_type: Style type (NORMAL_TEXT, HEADING_1, HEADING_2, etc.)
            alignment: Text alignment (START, CENTER, END, JUSTIFIED)
            line_spacing: Line spacing percentage (100 = single spacing)
            space_above: Space above paragraph in points
            space_below: Space below paragraph in points

        Returns:
            dict: {'success': bool, 'operation': 'UPDATE_PARAGRAPH_STYLE'}
        """
        try:
            paragraph_style = {}
            fields = []

            if named_style_type is not None:
                paragraph_style['namedStyleType'] = named_style_type
                fields.append('namedStyleType')
            if alignment is not None:
                paragraph_style['alignment'] = alignment
                fields.append('alignment')
            if line_spacing is not None:
                paragraph_style['lineSpacing'] = line_spacing
                fields.append('lineSpacing')
            if space_above is not None:
                paragraph_style['spaceAbove'] = {'magnitude': space_above, 'unit': 'PT'}
                fields.append('spaceAbove')
            if space_below is not None:
                paragraph_style['spaceBelow'] = {'magnitude': space_below, 'unit': 'PT'}
                fields.append('spaceBelow')

            if not fields:
                return {'success': False, 'error': 'No style properties specified', 'operation': 'UPDATE_PARAGRAPH_STYLE'}

            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'updateParagraphStyle': {
                            'range': {
                                'startIndex': start_index,
                                'endIndex': end_index
                            },
                            'paragraphStyle': paragraph_style,
                            'fields': ','.join(fields)
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'UPDATE_PARAGRAPH_STYLE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'UPDATE_PARAGRAPH_STYLE',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'UPDATE_PARAGRAPH_STYLE'}

    # ========================================
    # LIST OPERATIONS
    # ========================================

    def create_bullets(self, document_id, start_index, end_index, bullet_preset="BULLET_DISC_CIRCLE_SQUARE"):
        """
        Create a bulleted list from paragraphs.

        Args:
            document_id: The ID of the document
            start_index: Start index of range to convert to bullets
            end_index: End index of range to convert to bullets
            bullet_preset: Bullet style (BULLET_DISC_CIRCLE_SQUARE, BULLET_ARROW_DIAMOND_DISC, etc.)

        Returns:
            dict: {'success': bool, 'operation': 'CREATE_BULLETS'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'createParagraphBullets': {
                            'range': {
                                'startIndex': start_index,
                                'endIndex': end_index
                            },
                            'bulletPreset': bullet_preset
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'CREATE_BULLETS')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'CREATE_BULLETS',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CREATE_BULLETS'}

    def delete_bullets(self, document_id, start_index, end_index):
        """
        Remove bullets from paragraphs.

        Args:
            document_id: The ID of the document
            start_index: Start index of range to remove bullets from
            end_index: End index of range to remove bullets from

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_BULLETS'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'deleteParagraphBullets': {
                            'range': {
                                'startIndex': start_index,
                                'endIndex': end_index
                            }
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_BULLETS')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_BULLETS',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_BULLETS'}

    # ========================================
    # TABLE OPERATIONS
    # ========================================

    def insert_table(self, document_id, rows, columns, index):
        """
        Insert a table at a specific index.

        Args:
            document_id: The ID of the document
            rows: Number of rows
            columns: Number of columns
            index: Index where to insert the table

        Returns:
            dict: {'success': bool, 'operation': 'INSERT_TABLE', 'rows': int, 'columns': int}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'insertTable': {
                            'rows': rows,
                            'columns': columns,
                            'location': {'index': index}
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'INSERT_TABLE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'INSERT_TABLE',
                'rows': rows,
                'columns': columns,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'INSERT_TABLE'}

    def insert_table_row(self, document_id, table_start_index, row_index, insert_below=True):
        """
        Insert a row in a table.

        Args:
            document_id: The ID of the document
            table_start_index: Start index of the table
            row_index: Row index where to insert
            insert_below: True to insert below, False to insert above

        Returns:
            dict: {'success': bool, 'operation': 'INSERT_TABLE_ROW'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'insertTableRow': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_start_index},
                                'rowIndex': row_index,
                                'columnIndex': 0
                            },
                            'insertBelow': insert_below
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'INSERT_TABLE_ROW')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'INSERT_TABLE_ROW',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'INSERT_TABLE_ROW'}

    def insert_table_column(self, document_id, table_start_index, column_index, insert_right=True):
        """
        Insert a column in a table.

        Args:
            document_id: The ID of the document
            table_start_index: Start index of the table
            column_index: Column index where to insert
            insert_right: True to insert to the right, False to insert to the left

        Returns:
            dict: {'success': bool, 'operation': 'INSERT_TABLE_COLUMN'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'insertTableColumn': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_start_index},
                                'rowIndex': 0,
                                'columnIndex': column_index
                            },
                            'insertRight': insert_right
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'INSERT_TABLE_COLUMN')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'INSERT_TABLE_COLUMN',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'INSERT_TABLE_COLUMN'}

    def delete_table_row(self, document_id, table_start_index, row_index):
        """
        Delete a row from a table.

        Args:
            document_id: The ID of the document
            table_start_index: Start index of the table
            row_index: Row index to delete

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_TABLE_ROW'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'deleteTableRow': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_start_index},
                                'rowIndex': row_index,
                                'columnIndex': 0
                            }
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_TABLE_ROW')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_TABLE_ROW',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_TABLE_ROW'}

    def delete_table_column(self, document_id, table_start_index, column_index):
        """
        Delete a column from a table.

        Args:
            document_id: The ID of the document
            table_start_index: Start index of the table
            column_index: Column index to delete

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_TABLE_COLUMN'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'deleteTableColumn': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_start_index},
                                'rowIndex': 0,
                                'columnIndex': column_index
                            }
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_TABLE_COLUMN')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_TABLE_COLUMN',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_TABLE_COLUMN'}

    # ========================================
    # IMAGE OPERATIONS
    # ========================================

    def insert_inline_image(self, document_id, image_uri, index):
        """
        Insert an inline image at a specific index.

        Args:
            document_id: The ID of the document
            image_uri: URI of the image (must be publicly accessible or use Drive file ID)
            index: Index where to insert the image

        Returns:
            dict: {'success': bool, 'operation': 'INSERT_IMAGE', 'object_id': str}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'insertInlineImage': {
                            'uri': image_uri,
                            'location': {'index': index}
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'INSERT_IMAGE')

            if 'error' in result and not result.get('success', True):
                return result

            object_id = None
            if 'replies' in result and len(result['replies']) > 0:
                if 'insertInlineImage' in result['replies'][0]:
                    object_id = result['replies'][0]['insertInlineImage'].get('objectId')

            return {
                'success': True,
                'operation': 'INSERT_IMAGE',
                'object_id': object_id,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'INSERT_IMAGE'}

    def replace_image(self, document_id, image_object_id, new_image_uri):
        """
        Replace an existing image with a new one.

        Args:
            document_id: The ID of the document
            image_object_id: Object ID of the image to replace
            new_image_uri: URI of the new image

        Returns:
            dict: {'success': bool, 'operation': 'REPLACE_IMAGE'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'replaceImage': {
                            'imageObjectId': image_object_id,
                            'uri': new_image_uri
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'REPLACE_IMAGE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'REPLACE_IMAGE',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'REPLACE_IMAGE'}

    def delete_positioned_object(self, document_id, object_id):
        """
        Delete a positioned object (image, drawing, etc.).

        Args:
            document_id: The ID of the document
            object_id: Object ID to delete

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_OBJECT'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'deletePositionedObject': {
                            'objectId': object_id
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_OBJECT')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_OBJECT',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_OBJECT'}

    # ========================================
    # PAGE BREAK OPERATIONS
    # ========================================

    def insert_page_break(self, document_id, index):
        """
        Insert a page break at a specific index.

        Args:
            document_id: The ID of the document
            index: Index where to insert the page break

        Returns:
            dict: {'success': bool, 'operation': 'INSERT_PAGE_BREAK'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'insertPageBreak': {
                            'location': {'index': index}
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'INSERT_PAGE_BREAK')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'INSERT_PAGE_BREAK',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'INSERT_PAGE_BREAK'}

    # ========================================
    # NAMED RANGE OPERATIONS
    # ========================================

    def create_named_range(self, document_id, name, start_index, end_index):
        """
        Create a named range in the document.

        Args:
            document_id: The ID of the document
            name: Name for the range
            start_index: Start index of the range
            end_index: End index of the range

        Returns:
            dict: {'success': bool, 'operation': 'CREATE_NAMED_RANGE', 'named_range_id': str}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'createNamedRange': {
                            'name': name,
                            'range': {
                                'startIndex': start_index,
                                'endIndex': end_index
                            }
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'CREATE_NAMED_RANGE')

            if 'error' in result and not result.get('success', True):
                return result

            named_range_id = None
            if 'replies' in result and len(result['replies']) > 0:
                if 'createNamedRange' in result['replies'][0]:
                    named_range_id = result['replies'][0]['createNamedRange'].get('namedRangeId')

            return {
                'success': True,
                'operation': 'CREATE_NAMED_RANGE',
                'named_range_id': named_range_id,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CREATE_NAMED_RANGE'}

    def delete_named_range(self, document_id, named_range_id=None, name=None):
        """
        Delete a named range by ID or name.

        Args:
            document_id: The ID of the document
            named_range_id: ID of the named range to delete
            name: Name of the named range to delete (if ID not provided)

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_NAMED_RANGE'}
        """
        try:
            if not named_range_id and not name:
                return {'success': False, 'error': 'Must provide either named_range_id or name', 'operation': 'DELETE_NAMED_RANGE'}

            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            request_data = {}

            if named_range_id:
                request_data['namedRangeId'] = named_range_id
            else:
                request_data['name'] = name

            data = {
                'requests': [
                    {
                        'deleteNamedRange': request_data
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_NAMED_RANGE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_NAMED_RANGE',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_NAMED_RANGE'}

    # ========================================
    # HEADER/FOOTER OPERATIONS
    # ========================================

    def create_header(self, document_id, section_index=0, header_type="DEFAULT"):
        """
        Create a header in a section.

        Args:
            document_id: The ID of the document
            section_index: Index of the section (0 for first section)
            header_type: Type of header (DEFAULT, FIRST_PAGE_ONLY, EVEN_ODD)

        Returns:
            dict: {'success': bool, 'operation': 'CREATE_HEADER', 'header_id': str}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'createHeader': {
                            'sectionBreakLocation': {'index': section_index},
                            'type': header_type
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'CREATE_HEADER')

            if 'error' in result and not result.get('success', True):
                return result

            header_id = None
            if 'replies' in result and len(result['replies']) > 0:
                if 'createHeader' in result['replies'][0]:
                    header_id = result['replies'][0]['createHeader'].get('headerId')

            return {
                'success': True,
                'operation': 'CREATE_HEADER',
                'header_id': header_id,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CREATE_HEADER'}

    def create_footer(self, document_id, section_index=0, footer_type="DEFAULT"):
        """
        Create a footer in a section.

        Args:
            document_id: The ID of the document
            section_index: Index of the section (0 for first section)
            footer_type: Type of footer (DEFAULT, FIRST_PAGE_ONLY, EVEN_ODD)

        Returns:
            dict: {'success': bool, 'operation': 'CREATE_FOOTER', 'footer_id': str}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'createFooter': {
                            'sectionBreakLocation': {'index': section_index},
                            'type': footer_type
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'CREATE_FOOTER')

            if 'error' in result and not result.get('success', True):
                return result

            footer_id = None
            if 'replies' in result and len(result['replies']) > 0:
                if 'createFooter' in result['replies'][0]:
                    footer_id = result['replies'][0]['createFooter'].get('footerId')

            return {
                'success': True,
                'operation': 'CREATE_FOOTER',
                'footer_id': footer_id,
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CREATE_FOOTER'}

    def delete_header(self, document_id, header_id):
        """
        Delete a header.

        Args:
            document_id: The ID of the document
            header_id: ID of the header to delete

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_HEADER'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'deleteHeader': {
                            'headerId': header_id
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_HEADER')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_HEADER',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_HEADER'}

    def delete_footer(self, document_id, footer_id):
        """
        Delete a footer.

        Args:
            document_id: The ID of the document
            footer_id: ID of the footer to delete

        Returns:
            dict: {'success': bool, 'operation': 'DELETE_FOOTER'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'deleteFooter': {
                            'footerId': footer_id
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'DELETE_FOOTER')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'DELETE_FOOTER',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_FOOTER'}

    # ========================================
    # SECTION OPERATIONS
    # ========================================

    def insert_section_break(self, document_id, index, section_type="CONTINUOUS"):
        """
        Insert a section break.

        Args:
            document_id: The ID of the document
            index: Index where to insert the section break
            section_type: Type of section break (CONTINUOUS, NEXT_PAGE, SECTION_TYPE_UNSPECIFIED)

        Returns:
            dict: {'success': bool, 'operation': 'INSERT_SECTION_BREAK'}
        """
        try:
            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'insertSectionBreak': {
                            'location': {'index': index},
                            'sectionType': section_type
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'INSERT_SECTION_BREAK')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'INSERT_SECTION_BREAK',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'INSERT_SECTION_BREAK'}

    def update_section_style(self, document_id, start_index, end_index,
                             column_count=None, column_spacing=None,
                             margin_top=None, margin_bottom=None,
                             margin_left=None, margin_right=None):
        """
        Update section style.

        Args:
            document_id: The ID of the document
            start_index: Start index of the section range
            end_index: End index of the section range
            column_count: Number of columns
            column_spacing: Spacing between columns in points
            margin_top: Top margin in points
            margin_bottom: Bottom margin in points
            margin_left: Left margin in points
            margin_right: Right margin in points

        Returns:
            dict: {'success': bool, 'operation': 'UPDATE_SECTION_STYLE'}
        """
        try:
            section_style = {}
            fields = []

            if column_count is not None:
                section_style['columnCount'] = column_count
                fields.append('columnCount')
            if column_spacing is not None:
                section_style['columnSpacing'] = {'magnitude': column_spacing, 'unit': 'PT'}
                fields.append('columnSpacing')
            if margin_top is not None:
                section_style['marginTop'] = {'magnitude': margin_top, 'unit': 'PT'}
                fields.append('marginTop')
            if margin_bottom is not None:
                section_style['marginBottom'] = {'magnitude': margin_bottom, 'unit': 'PT'}
                fields.append('marginBottom')
            if margin_left is not None:
                section_style['marginLeft'] = {'magnitude': margin_left, 'unit': 'PT'}
                fields.append('marginLeft')
            if margin_right is not None:
                section_style['marginRight'] = {'magnitude': margin_right, 'unit': 'PT'}
                fields.append('marginRight')

            if not fields:
                return {'success': False, 'error': 'No style properties specified', 'operation': 'UPDATE_SECTION_STYLE'}

            url = f"{self.BASE_URL}/{document_id}:batchUpdate"
            data = {
                'requests': [
                    {
                        'updateSectionStyle': {
                            'range': {
                                'startIndex': start_index,
                                'endIndex': end_index
                            },
                            'sectionStyle': section_style,
                            'fields': ','.join(fields)
                        }
                    }
                ]
            }

            result = self._make_request('POST', url, data, 'UPDATE_SECTION_STYLE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'UPDATE_SECTION_STYLE',
                'document_id': document_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'UPDATE_SECTION_STYLE'}


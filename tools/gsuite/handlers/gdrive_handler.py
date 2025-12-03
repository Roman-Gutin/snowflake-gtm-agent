"""
Google Drive Handler for Snowflake UDFs

This module provides a comprehensive handler class for Google Drive API v3 operations.
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


class GDriveHandler:
    """
    Handler class for Google Drive API v3 operations in Snowflake UDFs.

    All methods use Service Account authentication via auth_helper.py
    and return structured JSON responses with success/error handling.
    """

    BASE_URL = "https://www.googleapis.com/drive/v3"
    UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"
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
    
    def _make_request(self, method, url, data=None, params=None, operation_name='API_CALL'):
        """
        Make HTTP request to Google Drive API with error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            url: Full URL to call
            data: Request body (for POST/PUT/PATCH)
            params: Query parameters
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
                response = requests.get(url, headers=headers, params=params, timeout=self.TIMEOUT)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params, timeout=self.TIMEOUT)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, params=params, timeout=self.TIMEOUT)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, params=params, timeout=self.TIMEOUT)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=self.TIMEOUT)
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}', 'operation': operation_name}
            
            if response.status_code >= 400:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'operation': operation_name
                }
            
            # DELETE returns 204 No Content
            if response.status_code == 204:
                return {'success': True}
            
            return response.json() if response.text else {}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation_name}
    
    # ========================================
    # FILE OPERATIONS
    # ========================================
    
    def list_files(self, query=None, page_size=100, order_by=None):
        """
        List files in Google Drive.
        
        Args:
            query: Search query (e.g., "name contains 'report'")
            page_size: Number of files to return (max 1000)
            order_by: Sort order (e.g., "modifiedTime desc")
            
        Returns:
            dict: {'success': bool, 'files': list, 'count': int}
        """
        try:
            url = f"{self.BASE_URL}/files"
            params = {
                'pageSize': min(page_size, 1000),
                'fields': 'files(id,name,mimeType,createdTime,modifiedTime,size,webViewLink,parents)'
            }
            
            if query:
                params['q'] = query
            if order_by:
                params['orderBy'] = order_by
            
            result = self._make_request('GET', url, params=params, operation_name='LIST_FILES')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            files = result.get('files', [])
            return {
                'success': True,
                'operation': 'LIST_FILES',
                'files': files,
                'count': len(files)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'LIST_FILES'}
    
    def get_file(self, file_id):
        """
        Get file metadata.
        
        Args:
            file_id: The ID of the file
            
        Returns:
            dict: File metadata
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}"
            params = {
                'fields': 'id,name,mimeType,createdTime,modifiedTime,size,webViewLink,parents,owners,permissions'
            }
            
            result = self._make_request('GET', url, params=params, operation_name='GET_FILE')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'GET_FILE',
                **result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'GET_FILE'}
    
    def create_folder(self, name, parent_id=None):
        """
        Create a folder in Google Drive.
        
        Args:
            name: Folder name
            parent_id: Parent folder ID (optional)
            
        Returns:
            dict: {'success': bool, 'id': str, 'webViewLink': str}
        """
        try:
            url = f"{self.BASE_URL}/files"
            data = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                data['parents'] = [parent_id]
            
            params = {'fields': 'id,name,webViewLink'}
            result = self._make_request('POST', url, data=data, params=params, operation_name='CREATE_FOLDER')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'CREATE_FOLDER',
                **result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'CREATE_FOLDER'}
    
    def copy_file(self, file_id, new_name=None, parent_id=None):
        """
        Copy a file.
        
        Args:
            file_id: ID of file to copy
            new_name: Name for the copy (optional)
            parent_id: Parent folder for the copy (optional)
            
        Returns:
            dict: {'success': bool, 'id': str, 'name': str}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}/copy"
            data = {}
            
            if new_name:
                data['name'] = new_name
            if parent_id:
                data['parents'] = [parent_id]
            
            params = {'fields': 'id,name,webViewLink'}
            result = self._make_request('POST', url, data=data, params=params, operation_name='COPY_FILE')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'COPY_FILE',
                **result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'COPY_FILE'}
    
    def delete_file(self, file_id):
        """
        Delete a file permanently.
        
        Args:
            file_id: ID of file to delete
            
        Returns:
            dict: {'success': bool}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}"
            result = self._make_request('DELETE', url, operation_name='DELETE_FILE')
            
            return {
                'success': True,
                'operation': 'DELETE_FILE',
                'file_id': file_id
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'DELETE_FILE'}
    
    def move_file(self, file_id, new_parent_id, old_parent_id=None):
        """
        Move a file to a different folder.
        
        Args:
            file_id: ID of file to move
            new_parent_id: ID of destination folder
            old_parent_id: ID of current parent (optional, will be retrieved if not provided)
            
        Returns:
            dict: {'success': bool}
        """
        try:
            # Get current parents if not provided
            if not old_parent_id:
                file_info = self.get_file(file_id)
                if not file_info.get('success'):
                    return file_info
                old_parent_id = ','.join(file_info.get('parents', []))
            
            url = f"{self.BASE_URL}/files/{file_id}"
            params = {
                'addParents': new_parent_id,
                'removeParents': old_parent_id,
                'fields': 'id,name,parents'
            }
            
            result = self._make_request('PATCH', url, params=params, operation_name='MOVE_FILE')
            
            if 'error' in result and not result.get('success', True):
                return result
            
            return {
                'success': True,
                'operation': 'MOVE_FILE',
                **result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'MOVE_FILE'}

    # ========================================
    # PERMISSION OPERATIONS
    # ========================================

    def share_file(self, file_id, email, role='reader', send_notification=False):
        """
        Share a file with a user.

        Args:
            file_id: ID of file to share
            email: Email address of user to share with
            role: Permission role (reader, writer, commenter, owner)
            send_notification: Whether to send email notification

        Returns:
            dict: {'success': bool, 'permissionId': str}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}/permissions"
            data = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            params = {
                'sendNotificationEmail': str(send_notification).lower(),
                'fields': 'id'
            }

            result = self._make_request('POST', url, data=data, params=params, operation_name='SHARE_FILE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'SHARE_FILE',
                'file_id': file_id,
                'email': email,
                'role': role,
                'permissionId': result.get('id')
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'SHARE_FILE'}

    def make_public(self, file_id, role='reader'):
        """
        Make a file publicly accessible.

        Args:
            file_id: ID of file to make public
            role: Permission role (reader, writer, commenter)

        Returns:
            dict: {'success': bool, 'webViewLink': str}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}/permissions"
            data = {
                'type': 'anyone',
                'role': role
            }
            params = {'fields': 'id'}

            result = self._make_request('POST', url, data=data, params=params, operation_name='MAKE_PUBLIC')

            if 'error' in result and not result.get('success', True):
                return result

            # Get the web view link
            file_info = self.get_file(file_id)

            return {
                'success': True,
                'operation': 'MAKE_PUBLIC',
                'file_id': file_id,
                'role': role,
                'webViewLink': file_info.get('webViewLink'),
                'permissionId': result.get('id')
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'MAKE_PUBLIC'}

    def list_permissions(self, file_id):
        """
        List all permissions for a file.

        Args:
            file_id: ID of file

        Returns:
            dict: {'success': bool, 'permissions': list}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}/permissions"
            params = {'fields': 'permissions(id,type,role,emailAddress,displayName)'}

            result = self._make_request('GET', url, params=params, operation_name='LIST_PERMISSIONS')

            if 'error' in result and not result.get('success', True):
                return result

            permissions = result.get('permissions', [])
            return {
                'success': True,
                'operation': 'LIST_PERMISSIONS',
                'file_id': file_id,
                'permissions': permissions,
                'count': len(permissions)
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'LIST_PERMISSIONS'}

    def remove_permission(self, file_id, permission_id):
        """
        Remove a permission from a file.

        Args:
            file_id: ID of file
            permission_id: ID of permission to remove

        Returns:
            dict: {'success': bool}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}/permissions/{permission_id}"
            result = self._make_request('DELETE', url, operation_name='REMOVE_PERMISSION')

            return {
                'success': True,
                'operation': 'REMOVE_PERMISSION',
                'file_id': file_id,
                'permission_id': permission_id
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'REMOVE_PERMISSION'}

    # ========================================
    # ADVANCED FILE OPERATIONS
    # ========================================

    def rename_file(self, file_id, new_name):
        """
        Rename a file.

        Args:
            file_id: ID of file to rename
            new_name: New name for the file

        Returns:
            dict: {'success': bool, 'id': str, 'name': str}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}"
            data = {'name': new_name}
            params = {'fields': 'id,name,webViewLink'}

            result = self._make_request('PATCH', url, data=data, params=params, operation_name='RENAME_FILE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'RENAME_FILE',
                **result
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'RENAME_FILE'}

    def update_file_description(self, file_id, description):
        """
        Update file description.

        Args:
            file_id: ID of file
            description: New description

        Returns:
            dict: {'success': bool}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}"
            data = {'description': description}
            params = {'fields': 'id,name,description'}

            result = self._make_request('PATCH', url, data=data, params=params, operation_name='UPDATE_DESCRIPTION')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'UPDATE_DESCRIPTION',
                **result
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'UPDATE_DESCRIPTION'}

    def search_files(self, query, page_size=100):
        """
        Search for files using a query string.

        Args:
            query: Search query (e.g., "name contains 'report' and mimeType='application/pdf'")
            page_size: Number of results to return

        Returns:
            dict: {'success': bool, 'files': list, 'count': int}
        """
        return self.list_files(query=query, page_size=page_size, order_by='modifiedTime desc')

    def get_file_metadata(self, file_id):
        """
        Get comprehensive file metadata including permissions and sharing info.

        Args:
            file_id: The ID of the file

        Returns:
            dict: Comprehensive file metadata
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}"
            params = {
                'fields': 'id,name,mimeType,description,createdTime,modifiedTime,size,webViewLink,webContentLink,iconLink,thumbnailLink,parents,owners,lastModifyingUser,shared,ownedByMe,capabilities,permissions,sharingUser,viewedByMe,viewedByMeTime'
            }

            result = self._make_request('GET', url, params=params, operation_name='GET_FILE_METADATA')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'GET_FILE_METADATA',
                **result
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'GET_FILE_METADATA'}

    def export_file(self, file_id, mime_type):
        """
        Export a Google Workspace file to a different format.

        Args:
            file_id: ID of file to export
            mime_type: Target MIME type (e.g., 'application/pdf', 'text/plain')

        Returns:
            dict: {'success': bool, 'content': bytes} or error
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}/export"
            params = {'mimeType': mime_type}

            token = self._get_access_token()
            headers = {'Authorization': f'Bearer {token}'}

            response = requests.get(url, headers=headers, params=params, timeout=self.TIMEOUT)

            if response.status_code >= 400:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'operation': 'EXPORT_FILE'
                }

            return {
                'success': True,
                'operation': 'EXPORT_FILE',
                'file_id': file_id,
                'mime_type': mime_type,
                'size': len(response.content),
                'content_preview': response.content[:100].decode('utf-8', errors='ignore') if response.content else ''
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'EXPORT_FILE'}

    # ========================================
    # TRASH OPERATIONS
    # ========================================

    def trash_file(self, file_id):
        """
        Move a file to trash (soft delete).

        Args:
            file_id: ID of file to trash

        Returns:
            dict: {'success': bool}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}"
            data = {'trashed': True}
            params = {'fields': 'id,name,trashed'}

            result = self._make_request('PATCH', url, data=data, params=params, operation_name='TRASH_FILE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'TRASH_FILE',
                **result
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'TRASH_FILE'}

    def untrash_file(self, file_id):
        """
        Restore a file from trash.

        Args:
            file_id: ID of file to restore

        Returns:
            dict: {'success': bool}
        """
        try:
            url = f"{self.BASE_URL}/files/{file_id}"
            data = {'trashed': False}
            params = {'fields': 'id,name,trashed'}

            result = self._make_request('PATCH', url, data=data, params=params, operation_name='UNTRASH_FILE')

            if 'error' in result and not result.get('success', True):
                return result

            return {
                'success': True,
                'operation': 'UNTRASH_FILE',
                **result
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'UNTRASH_FILE'}

    def list_trashed_files(self, page_size=100):
        """
        List files in trash.

        Args:
            page_size: Number of files to return

        Returns:
            dict: {'success': bool, 'files': list}
        """
        return self.list_files(query='trashed=true', page_size=page_size, order_by='modifiedTime desc')

    def empty_trash(self):
        """
        Permanently delete all files in trash.
        WARNING: This action cannot be undone!

        Returns:
            dict: {'success': bool}
        """
        try:
            url = f"{self.BASE_URL}/files/trash"
            result = self._make_request('DELETE', url, operation_name='EMPTY_TRASH')

            return {
                'success': True,
                'operation': 'EMPTY_TRASH',
                'message': 'All trashed files permanently deleted'
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'EMPTY_TRASH'}

    # ========================================
    # FOLDER-SPECIFIC OPERATIONS
    # ========================================

    def list_folder_contents(self, folder_id, page_size=100, order_by=None):
        """
        List all files and folders within a specific folder.

        Args:
            folder_id: ID of the folder to list contents from
            page_size: Maximum number of items to return (default: 100)
            order_by: Sort order (e.g., 'name', 'modifiedTime desc')

        Returns:
            dict: List of files/folders with metadata
        """
        query = f"'{folder_id}' in parents and trashed=false"
        return self.list_files(query=query, page_size=page_size, order_by=order_by)

    def get_folder_metadata(self, folder_id):
        """
        Get detailed metadata for a folder including permissions and sharing.

        Args:
            folder_id: ID of the folder

        Returns:
            dict: Comprehensive folder metadata
        """
        return self.get_file_metadata(folder_id)

    def update_folder(self, folder_id, name=None, description=None, folder_color_rgb=None):
        """
        Update folder properties (name, description, color).

        Args:
            folder_id: ID of the folder to update
            name: New folder name (optional)
            description: New folder description (optional)
            folder_color_rgb: Folder color in RGB hex format (e.g., '#ff0000') (optional)

        Returns:
            dict: Updated folder metadata
        """
        url = f"{self.BASE_URL}/files/{folder_id}"

        # Build update payload
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        if folder_color_rgb is not None:
            update_data['folderColorRgb'] = folder_color_rgb

        if not update_data:
            return {
                'success': False,
                'error': 'No update fields provided',
                'operation': 'UPDATE_FOLDER'
            }

        params = {
            'fields': 'id,name,description,mimeType,folderColorRgb,modifiedTime,webViewLink'
        }

        result = self._make_request('PATCH', url, data=update_data, params=params, operation_name='UPDATE_FOLDER')

        if result.get('success') is False:
            return result

        return {
            'success': True,
            'folder_id': result.get('id'),
            'name': result.get('name'),
            'description': result.get('description'),
            'folder_color': result.get('folderColorRgb'),
            'modified_time': result.get('modifiedTime'),
            'web_view_link': result.get('webViewLink')
        }

    def share_folder(self, folder_id, email, role='reader', send_notification=False):
        """
        Share a folder with a user (alias for share_file, but more explicit for folders).

        Args:
            folder_id: ID of the folder to share
            email: Email address of the user to share with
            role: Permission role ('reader', 'writer', 'commenter', 'owner')
            send_notification: Whether to send email notification

        Returns:
            dict: Permission details
        """
        return self.share_file(folder_id, email, role, send_notification)

    def create_file(self, name, mime_type='text/plain', parent_id=None, content=None):
        """
        Create a new file in Google Drive.

        Args:
            name: Name of the file
            mime_type: MIME type of the file (default: 'text/plain')
            parent_id: Parent folder ID (optional)
            content: File content as string (optional, for simple text files)

        Returns:
            dict: Created file metadata
        """
        metadata = {
            'name': name,
            'mimeType': mime_type
        }

        if parent_id:
            metadata['parents'] = [parent_id]

        # For simple file creation without content upload
        url = f"{self.BASE_URL}/files"
        params = {
            'fields': 'id,name,mimeType,webViewLink,createdTime'
        }

        result = self._make_request('POST', url, data=metadata, params=params, operation_name='CREATE_FILE')

        if result.get('success') is False:
            return result

        return {
            'success': True,
            'file_id': result.get('id'),
            'name': result.get('name'),
            'mime_type': result.get('mimeType'),
            'web_view_link': result.get('webViewLink'),
            'created_time': result.get('createdTime')
        }

    def update_file_content(self, file_id, content, mime_type='text/plain'):
        """
        Update the content of an existing file.

        Args:
            file_id: ID of the file to update
            content: New file content as string
            mime_type: MIME type of the content

        Returns:
            dict: Updated file metadata
        """
        # Note: This is a simplified version. For binary files, use multipart upload
        url = f"{self.UPLOAD_URL}/{file_id}"
        params = {
            'uploadType': 'media',
            'fields': 'id,name,modifiedTime,webViewLink'
        }

        try:
            token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': mime_type
            }

            response = requests.patch(url, headers=headers, data=content.encode('utf-8'), params=params, timeout=self.TIMEOUT)

            if response.status_code >= 400:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'operation': 'UPDATE_FILE_CONTENT'
                }

            result = response.json()
            return {
                'success': True,
                'file_id': result.get('id'),
                'name': result.get('name'),
                'modified_time': result.get('modifiedTime'),
                'web_view_link': result.get('webViewLink')
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': 'UPDATE_FILE_CONTENT'}

    def get_folder_tree(self, folder_id, max_depth=2):
        """
        Get folder structure as a tree (folder and its subfolders).

        Args:
            folder_id: ID of the root folder
            max_depth: Maximum depth to traverse (default: 2)

        Returns:
            dict: Folder tree structure
        """
        def get_children(parent_id, current_depth):
            if current_depth >= max_depth:
                return []

            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            result = self.list_files(query=query, page_size=100)

            if not result.get('success', True) or 'files' not in result:
                return []

            children = []
            for folder in result['files']:
                folder_info = {
                    'id': folder['id'],
                    'name': folder['name'],
                    'web_view_link': folder.get('webViewLink'),
                    'children': get_children(folder['id'], current_depth + 1)
                }
                children.append(folder_info)

            return children

        # Get root folder info
        root_info = self.get_file(folder_id)
        if root_info.get('success') is False:
            return root_info

        return {
            'success': True,
            'folder': {
                'id': root_info.get('file_id'),
                'name': root_info.get('name'),
                'web_view_link': root_info.get('web_view_link'),
                'children': get_children(folder_id, 0)
            }
        }

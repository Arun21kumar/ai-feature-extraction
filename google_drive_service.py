"""
Google Drive Service Module

Handles authentication and file operations with Google Drive API v3.
Supports uploading files, setting permissions, and generating shareable links.

This version is updated to use OAuth 2.0 Client ID for personal Gmail accounts.

Author: AI Feature Extraction Team
Date: January 2026
"""

import logging
import os
from pathlib import Path
from typing import Optional, Tuple

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """
    Service class for Google Drive API operations.
    
    Handles file uploads, permission management, and link generation
    using OAuth 2.0 for personal user accounts.
    """
    
    # Google Drive API scopes - also include Gmail scope to ensure token has all permissions
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    def __init__(self, credentials_path: str, token_path: str = "token.json"):
        """
        Initialize Google Drive service with OAuth 2.0 authentication.
        
        Args:
            credentials_path: Path to the OAuth 2.0 client secrets JSON file.
            token_path: Path to store the user's token.
                            
        Raises:
            FileNotFoundError: If credentials file doesn't exist.
            Exception: If authentication fails.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Client secrets file not found: {self.credentials_path}")
        
        creds = self._authenticate()
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive service authenticated successfully")
        except Exception as e:
            logger.error(f"Failed to build Google Drive service: {e}")
            raise

    def _authenticate(self) -> Credentials:
        """
        Handles the OAuth 2.0 authentication flow.
        
        Loads credentials from token_path if available, otherwise initiates
        the Installed App Flow to get user authorization.
        
        Returns:
            A google.oauth2.credentials.Credentials object.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Credentials expired, refreshing...")
                creds.refresh(Request())
            else:
                logger.info("No valid credentials found, running OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {self.token_path}")
            
        return creds
    
    def upload_file(
        self,
        file_path: str,
        folder_id: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Upload a file to Google Drive and return its shareable link and ID.
        
        Args:
            file_path: Local path to file to upload
            folder_id: Google Drive folder ID to upload to (optional)
            file_name: Name for the file in Google Drive (defaults to original filename)
            
        Returns:
            A tuple containing (shareable_link, file_id)
            
        Raises:
            FileNotFoundError: If local file doesn't exist
            HttpError: If Google Drive API call fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file name and MIME type
        if not file_name:
            file_name = os.path.basename(file_path)
        
        mime_type = self._get_mime_type(file_path)
        
        logger.info(f"Uploading file: {file_name} (MIME: {mime_type})")
        
        try:
            # Prepare file metadata
            file_metadata = {'name': file_name}
            
            # Add parent folder if specified
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            web_view_link = file.get('webViewLink')
            
            logger.info(f"File uploaded successfully. ID: {file_id}")
            
            # Make file public (anyone with the link can view)
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            logger.info(f"File made public. Link: {web_view_link}")
            
            return web_view_link, file_id
            
        except HttpError as e:
            logger.error(f"HTTP error during file upload: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during upload: {e}")
            raise
    
    def get_public_link(self, file_id: str) -> Optional[str]:
        """
        Get the public link of a file by its ID.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Public shareable link to the file, or None if not found or not public
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink, webContentLink'
            ).execute()
            
            # Prefer webViewLink for viewing in browser
            shareable_link = file.get('webViewLink') or file.get('webContentLink')
            
            logger.info(f"Retrieved public link: {shareable_link}")
            return shareable_link
            
        except HttpError as e:
            logger.error(f"Failed to get public link for file {file_id}: {e}")
            return None
    
    def _get_mime_type(self, file_path: str) -> str:
        """
        Determine MIME type based on file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            MIME type string
        """
        extension = Path(file_path).suffix.lower()
        
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
        }
        
        return mime_types.get(extension, 'application/octet-stream')
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"File deleted successfully: {file_id}")
            return True
        except HttpError as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False
    
    def list_files(self, folder_id: Optional[str] = None, page_size: int = 100) -> list:
        """
        List files in Google Drive folder.
        
        Args:
            folder_id: Google Drive folder ID (None for root)
            page_size: Maximum number of files to return
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            query = f"'{folder_id}' in parents" if folder_id else None
            
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, createdTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files")
            return files
            
        except HttpError as e:
            logger.error(f"Failed to list files: {e}")
            return []


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test the service
    try:
        drive_service = GoogleDriveService(credentials_path="credentials.json")
        print("✓ Google Drive service initialized successfully")
        
        # List files (optional)
        # files = drive_service.list_files()
        # print(f"Found {len(files)} files in Drive")
        
    except Exception as e:
        print(f"✗ Error: {e}")

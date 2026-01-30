"""
Gmail Service Module

Handles authentication and email operations with Gmail API.
Supports sending emails with HTML content and attachments.

This version is updated to use OAuth 2.0 Client ID for personal Gmail accounts.

Author: AI Feature Extraction Team
Date: January 2026
"""

import base64
import logging
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailService:
    """
    Service class for Gmail API operations.
    
    Handles email composition and sending with support for HTML content
    and file attachments using OAuth 2.0 for personal user accounts.
    """
    
    # Gmail API scopes - also include Drive scope to ensure token has all permissions
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_path: str, token_path: str = "token.json", sender_email: Optional[str] = None):
        """
        Initialize Gmail service with OAuth 2.0 authentication.
        
        Args:
            credentials_path: Path to the OAuth 2.0 client secrets JSON file.
            token_path: Path to store the user's token.
            sender_email: Email address to send from. If None, it will be
                          inferred from the authenticated user, but it's
                          recommended to set it from the environment.
                         
        Raises:
            FileNotFoundError: If credentials file doesn't exist.
            ValueError: If sender email is not provided.
            Exception: If authentication fails.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Client secrets file not found: {self.credentials_path}")

        # Get sender email
        self.sender_email = sender_email or os.getenv('GMAIL_SENDER_EMAIL')
        
        if not self.sender_email:
            raise ValueError(
                "Sender email not provided. "
                "Set GMAIL_SENDER_EMAIL environment variable or pass sender_email parameter."
            )

        creds = self._authenticate()
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service authenticated successfully")
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
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

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> dict:
        """
        Send a simple email without attachments.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional, overrides plain text)
            cc: CC email address (optional)
            bcc: BCC email address (optional)
            
        Returns:
            Gmail API response dictionary
            
        Raises:
            HttpError: If Gmail API call fails
        """
        logger.info(f"Sending email to: {to}")
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.sender_email
            message['To'] = to
            message['Subject'] = subject
            
            if cc:
                message['Cc'] = cc
            if bcc:
                message['Bcc'] = bcc
            
            # Add plain text body
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                message.attach(MIMEText(html_body, 'html'))
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}
            
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            logger.info(f"Email sent successfully. Message ID: {result.get('id')}")
            return result
            
        except HttpError as e:
            logger.error(f"HTTP error sending email: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
    
    def send_email_with_attachment(
        self,
        to: str,
        subject: str,
        html_body: str,
        attachment_path: str,
        body: Optional[str] = None,
        cc: Optional[str] = None
    ) -> dict:
        """
        Send an email with file attachment.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachment_path: Path to file to attach
            body: Plain text email body (optional)
            cc: CC email address (optional)
            
        Returns:
            Gmail API response dictionary
            
        Raises:
            FileNotFoundError: If attachment file doesn't exist
            HttpError: If Gmail API call fails
        """
        if not os.path.exists(attachment_path):
            raise FileNotFoundError(f"Attachment not found: {attachment_path}")
        
        logger.info(f"Sending email with attachment to: {to}")
        logger.info(f"Attachment: {os.path.basename(attachment_path)}")
        
        try:
            # Create message
            message = MIMEMultipart('mixed')
            message['From'] = self.sender_email
            message['To'] = to
            message['Subject'] = subject
            
            if cc:
                message['Cc'] = cc
            
            # Create alternative part for text/html
            msg_alternative = MIMEMultipart('alternative')
            
            # Add plain text body if provided
            if body:
                msg_alternative.attach(MIMEText(body, 'plain'))
            
            # Add HTML body
            msg_alternative.attach(MIMEText(html_body, 'html'))
            
            message.attach(msg_alternative)
            
            # Add attachment
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read())
            
            attachment_filename = os.path.basename(attachment_path)
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=attachment_filename
            )
            message.attach(attachment)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}
            
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            logger.info(f"Email with attachment sent successfully. Message ID: {result.get('id')}")
            return result
            
        except HttpError as e:
            logger.error(f"HTTP error sending email with attachment: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to send email with attachment: {e}")
            raise
    
    def send_email_with_multiple_attachments(
        self,
        to: str,
        subject: str,
        html_body: str,
        attachment_paths: list,
        body: Optional[str] = None
    ) -> dict:
        """
        Send an email with multiple file attachments.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachment_paths: List of paths to files to attach
            body: Plain text email body (optional)
            
        Returns:
            Gmail API response dictionary
        """
        logger.info(f"Sending email with {len(attachment_paths)} attachments to: {to}")
        
        try:
            # Create message
            message = MIMEMultipart('mixed')
            message['From'] = self.sender_email
            message['To'] = to
            message['Subject'] = subject
            
            # Create alternative part for text/html
            msg_alternative = MIMEMultipart('alternative')
            
            if body:
                msg_alternative.attach(MIMEText(body, 'plain'))
            
            msg_alternative.attach(MIMEText(html_body, 'html'))
            message.attach(msg_alternative)
            
            # Add attachments
            for attachment_path in attachment_paths:
                if not os.path.exists(attachment_path):
                    logger.warning(f"Attachment not found, skipping: {attachment_path}")
                    continue
                
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                
                attachment_filename = os.path.basename(attachment_path)
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=attachment_filename
                )
                message.attach(attachment)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}
            
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            logger.info(f"Email with attachments sent successfully. Message ID: {result.get('id')}")
            return result
            
        except HttpError as e:
            logger.error(f"HTTP error sending email with attachments: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to send email with attachments: {e}")
            raise


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test the service
    try:
        gmail_service = GmailService(
            credentials_path='path/to/credentials.json',  # Update this path
            token_path='path/to/token.json'               # Update this path
        )
        print("✓ Gmail service initialized successfully")
        print(f"  Sender: {gmail_service.sender_email}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nNote: Gmail API requires:")
        print("  1. OAuth 2.0 Client ID for installed applications")
        print("  2. GMAIL_SENDER_EMAIL environment variable set")
        print("  3. Proper OAuth scopes configured in Google Cloud Console")

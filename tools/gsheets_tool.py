"""
Google Sheets Import Tool
-------------------------
Imports CSV data into a new Google Sheet using Google Sheets API.
"""
import os
import csv
import logging
from pathlib import Path
from typing import Dict, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Import file manager
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.file_manager import file_manager

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_google_sheets_service():
    """Get Google Sheets API service with authentication."""
    creds = None
    token_path = Path('token.json')
    credentials_path = Path('credentials.json')
    
    # The file token.json stores the user's access and refresh tokens
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                return {
                    "success": False,
                    "error": "credentials.json not found. Please set up Google Sheets API."
                }
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('sheets', 'v4', credentials=creds)


def import_csv_to_google_sheets(csv_path: str, sheet_title: str = "Employee Data") -> Dict[str, Any]:
    """
    Import CSV data into a new Google Sheet.
    
    Args:
        csv_path: Path to the CSV file
        sheet_title: Title for the Google Sheet
        
    Returns:
        Dictionary with success status, sheet URL, and metadata
    """
    try:
        # Resolve CSV path
        csv_file = Path(csv_path)
        if not csv_file.is_absolute():
            csv_file = file_manager.get_file_path(csv_file.name, subdir="csv")
        
        if not csv_file.exists():
            return {
                "success": False,
                "error": f"CSV file not found: {csv_file}"
            }
        
        # Get Google Sheets service
        service_result = get_google_sheets_service()
        if isinstance(service_result, dict) and not service_result.get("success", True):
            return service_result
        
        service = service_result
        
        # Read CSV data
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            data = list(csv_reader)
        
        # Create new spreadsheet
        spreadsheet = {
            'properties': {
                'title': sheet_title
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        spreadsheet_url = spreadsheet.get('spreadsheetUrl')
        
        # Update with data
        body = {
            'values': data
        }
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Format header row
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.8,
                            'green': 0.8,
                            'blue': 0.8
                        },
                        'textFormat': {
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        # Auto-resize columns
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'requests': [{
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': len(data[0]) if data else 5
                        }
                    }
                }]
            }
        ).execute()
        
        logger.info(f"✅ Created Google Sheet: {spreadsheet_url}")
        
        return {
            "success": True,
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": spreadsheet_url,
            "title": sheet_title,
            "rows": len(data),
            "message": f"Successfully created Google Sheet: {sheet_title}"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to import to Google Sheets: {e}")
        return {
            "success": False,
            "error": str(e)
        }
"""
Google Sheets API integration.
Provides data export functionality to Google Sheets.
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def setup_google_sheets_client():
    """
    Setup Google Sheets client with service account credentials.
    
    Returns:
        gspread.Client: Authorized Google Sheets client
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    creds = ServiceAccountCredentials.from_json_keyfile_name('google-sheets-auth.json', scope)
    client = gspread.authorize(creds)
    
    return client

def export_to_google_sheets(data, spreadsheet_id, worksheet_name):
    """
    Export data to specified Google Sheets worksheet.
    
    Args:
        data: List of dictionaries to export
        spreadsheet_id: Google Sheets spreadsheet ID
        worksheet_name: Name of worksheet to update
        
    Returns:
        bool: True if export successful
    """
    client = setup_google_sheets_client()
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    
    # Clear existing data
    worksheet.clear()
    
    # Export new data
    if data:
        # Convert data to list format for Google Sheets
        headers = list(data[0].keys())
        worksheet.append_row(headers)
        
        for row in data:
            worksheet.append_row(list(row.values()))
    
    return True

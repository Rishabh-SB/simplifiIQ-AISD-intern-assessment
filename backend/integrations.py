import os
import json
import base64
import time
from datetime import datetime
import resend
from pydantic import BaseModel, EmailStr, Field
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# --- 1. DATA VALIDATION LAYER ---
class LeadIntakeSchema(BaseModel):
    """Enforces strict structural boundaries on incoming raw payload data."""
    name: str = Field(..., min_length=1, max_length=100, description="Lead name cannot be empty")
    email: EmailStr = Field(..., description="Must be a structurally valid email address")
    company: str = Field(..., min_length=1, max_length=100, description="Company name cannot be empty")

# --- 2. RETRY UTILITY (EXPONENTIAL BACKOFF) ---
def execute_with_retry(api_call_func, max_retries=3, initial_delay=2):
    """
    Executes a network-bound function with exponential backoff.
    Safe for rate limits (429) and temporary remote server degradation (5xx).
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return api_call_func()
        except Exception as e:
            # Check for known Google API HTTP errors
            if isinstance(e, HttpError):
                status_code = e.resp.status
                # Do not retry client bugs like missing permissions (403) or bad requests (400)
                if status_code in [400, 401, 403, 404]:
                    print(f"Unrecoverable API Error ({status_code}): {e.reason}. Skipping retries.")
                    raise e
            
            print(f"[Attempt {attempt}/{max_retries}] Network/API blip encountered: {str(e)}")
            if attempt == max_retries:
                raise e
            
            print(f"Sleeping {delay}s before retrying...")
            time.sleep(delay)
            delay *= 2  # Double the wait time for the next round

# --- 3. ROBUST SYSTEM CORE INTEGRATIONS ---
def get_google_credentials():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Critical configuration error: Missing OAuth2 environment keys.")
        
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
    )
    
    # Ensure token fresh baseline validation
    creds.refresh(Request())
    return creds

def archive_pdf_to_drive(pdf_path: str) -> str:
    if not pdf_path or not os.path.exists(pdf_path):
        print("Upload Aborted: Local target report PDF file path does not exist.")
        return ""
        
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id: 
        print("Configuration Warning: GOOGLE_DRIVE_FOLDER_ID environment string missing.")
        return ""
        
    try:
        creds = get_google_credentials()
        service = build("drive", "v3", credentials=creds)
        
        file_metadata = {"name": os.path.basename(pdf_path), "parents": [folder_id]}
        media = MediaFileUpload(pdf_path, mimetype="application/pdf", resumable=True)
        
        # Wrap the actual drive transmission execute network task inside our retry wrapper
        uploaded_file = execute_with_retry(
            lambda: service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        )
        
        file_id = uploaded_file.get("id")
        print(f"PDF successfully archived to personal Drive: {file_id}")
        return file_id
    except Exception as e:
        print(f"Hard Failure: Drive archival failed after retries: {e}")
        return ""

def log_to_google_sheet(name: str, email: str, company: str, status: str):
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id: 
        print("Configuration Warning: GOOGLE_SHEET_ID system key is missing.")
        return
    try:
        creds = get_google_credentials()
        service = build("sheets", "v4", credentials=creds)
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        body = {"values": [[name, email, company, timestamp, status]]}
        
        execute_with_retry(
            lambda: service.spreadsheets().values().append(
                spreadsheetId=sheet_id, range="Sheet1!A:E",
                valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body=body
            ).execute()
        )
        print("Core metrics log row appended to spreadsheet.")
    except Exception as e:
        print(f"Hard Failure: Row logging failed to commit: {e}")

def send_outreach_email(recipient_email: str, company_name: str, pdf_path: str) -> bool:
    resend_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
    if not resend_key:
        print("Configuration Warning: RESEND_API_KEY identifier is missing.")
        return False
        
    try:
        resend.api_key = resend_key
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Attachment missing at runtime reference: {pdf_path}")
            
        with open(pdf_path, "rb") as pdf_file:
            encoded_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
            
        params = {
            "from": f"SimplifIQ (MOCK) Intelligence Team <{from_email}>",
            "to": [recipient_email],
            "subject": f"Your Custom AI Automation Audit — {company_name}",
            "html": f"<h3>Hello,</h3><p>Please find your custom automation advisory report attached below.</p><br/><p>Best regards,<br/><strong>SimplifIQ (MOCK) Team</strong></p>",
            "attachments": [{"content": encoded_pdf, "filename": os.path.basename(pdf_path)}]
        }
        
        execute_with_retry(lambda: resend.Emails.send(params))
        print("Customer outreach mail delivery success.")
        return True
    except Exception as e:
        print(f"Hard Failure: Email failed to dispatch via Resend API: {e}")
        return False
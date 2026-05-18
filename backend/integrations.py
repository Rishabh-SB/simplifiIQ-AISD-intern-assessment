import os
import json
import base64
import time  # Imported for backoff delays
from datetime import datetime
import resend
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_google_credentials():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing OAuth2 user configuration inside backend environment keys.")
        
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
    
    creds.refresh(Request())
    return creds
    
    # Force refresh token handshake to validate the session
    creds.refresh(Request())
    return creds

def archive_pdf_to_drive(pdf_path: str) -> str:
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id: 
        print("⚠️ GOOGLE_DRIVE_FOLDER_ID is missing from your environment setup.")
        return ""
    try:
        creds = get_google_credentials()
        # Authenticates directly as sbrishabhmail@gmail.com
        service = build("drive", "v3", credentials=creds)
        
        file_metadata = {
            "name": os.path.basename(pdf_path), 
            "parents": [folder_id]
        }
        
        media = MediaFileUpload(pdf_path, mimetype="application/pdf", resumable=True)
        
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields="id"
        ).execute()
        
        file_id = uploaded_file.get("id")
        print(f"✅ PDF successfully archived to your personal Drive! File ID: {file_id}")
        return file_id
        
    except Exception as e:
        print(f"❌ Failed archiving PDF to Google Drive via OAuth: {e}")
        return ""

def log_to_google_sheet(name: str, email: str, company: str, status: str):
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id: return
    try:
        creds = get_google_credentials()
        service = build("sheets", "v4", credentials=creds)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        body = {"values": [[name, email, company, timestamp, status]]}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="Sheet1!A:E",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body=body
        ).execute()
        print("✅ Data row successfully logged to your tracking sheet!")
    except Exception as e:
        print(f"❌ Failed logging row data to Google Sheets: {e}")

def send_outreach_email(recipient_email: str, company_name: str, pdf_path: str):
    resend_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
    if not resend_key: 
        print("❌ Resend API Key missing. Skipping email transmission.")
        return
        
    resend.api_key = resend_key
    
    try:
        with open(pdf_path, "rb") as pdf_file:
            encoded_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Failed to read or encode PDF asset: {e}")
        return

    params = {
        "from": f"SimplifIQ Intelligence Team <{from_email}>",
        "to": [recipient_email],
        "subject": f"Your Custom AI Automation Audit — {company_name}",
        "html": f"<h3>Hello,</h3><p>Thank you for requesting an engineering assessment review for <strong>{company_name}</strong>.</p><p>Please find your custom automation advisory report attached below.</p><br/><p>Best regards,<br/><strong>SimplifIQ Team</strong></p>",
        "attachments": [{"content": encoded_pdf, "filename": os.path.basename(pdf_path)}],
    }

    # Resiliency Loop: Exponential Backoff Retry Strategy
    max_retries = 3
    delay = 2  # Starting delay in seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"📧 Sending email via Resend (Attempt {attempt}/{max_retries})...")
            resend.Emails.send(params)
            print("✅ Email successfully transmitted through Resend infrastructure!")
            return  # Success! Break out of the function entirely.
            
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed transmitting email: {e}")
            if attempt == max_retries:
                print("❌ Maximum email transmission retries exceeded. Escalating error block.")
                raise e  # Re-raise error to let main.py handle the pipeline status update
            
            print(f"🔄 Temporary network or DNS anomaly detected. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Double the wait time for the next try (2s -> 4s)
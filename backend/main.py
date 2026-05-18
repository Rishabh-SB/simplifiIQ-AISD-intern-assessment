import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

from scraper import enrich_company_data
from reporter import generate_pdf_report
from integrations import log_to_google_sheet, archive_pdf_to_drive, send_outreach_email

load_dotenv()

app = FastAPI(title="SimplifIQ Lead Automation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeadSubmission(BaseModel):
    name: str
    email: EmailStr
    company_name: str
    company_url: str

async def process_lead_pipeline(lead: LeadSubmission):
    print(f"🚀 Initializing automated sequence for: {lead.company_name}")
    pdf_path = None
    try:
        # Step 1: Scrape and Enrich
        enriched_info = await enrich_company_data(lead.company_name, lead.company_url)
        # Step 2: Generate PDF Audit
        pdf_path = generate_pdf_report(lead.company_name, enriched_info)
        # Step 3 & 4: Archive and Email
        archive_pdf_to_drive(pdf_path)
        send_outreach_email(lead.email, lead.company_name, pdf_path)
        # Step 5: Log operational success
        log_to_google_sheet(lead.name, lead.email, lead.company_name, status="Processed & Emailed")
    except Exception as err:
        print(f"❌ Error within background data loop: {err}")
        log_to_google_sheet(lead.name, lead.email, lead.company_name, status=f"Error: {str(err)}")
    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.post("/api/leads")
async def register_lead(lead: LeadSubmission, background_tasks: BackgroundTasks):
    if not lead.name or not lead.email or not lead.company_name:
        raise HTTPException(status_code=400, detail="Missing critical input parameters.")
    background_tasks.add_task(process_lead_pipeline, lead)
    return {"status": "success", "message": "Pipeline triggered successfully."}

@app.get("/")
def health_check():
    return {"status": "healthy"}
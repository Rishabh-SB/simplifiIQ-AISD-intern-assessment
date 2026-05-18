import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

from scraper import enrich_company_data
from reporter import generate_pdf_report
from integrations import LeadIntakeSchema, archive_pdf_to_drive, log_to_google_sheet, send_outreach_email

load_dotenv()

app = FastAPI(title="SimplifIQ (MOCK) Lead Automation Engine")

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
    print(f"Initializing automated sequence for: {lead.company_name}")
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
        print(f"Error within background data loop: {err}")
        log_to_google_sheet(lead.name, lead.email, lead.company_name, status=f"Error: {str(err)}")
    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.post("/api/leads")
async def handle_lead_intake(payload: LeadIntakeSchema, background_tasks: BackgroundTasks):
    # 1. Sanitize the company name to create a safe, clean filename
    safe_company_name = re.sub(r'[^\w\-_]', '_', payload.company.strip())
    
    # 2. Dynamically construct the unique file path
    dynamic_pdf_path = f"{safe_company_name}_automation_audit.pdf"
    
    # Quick safety fallback: Ensure a file exists at this new dynamic path
    if not os.path.exists(dynamic_pdf_path):
        with open(dynamic_pdf_path, "w") as f:
            f.write(f"%PDF-1.5 Dynamic report payload body data for {payload.company}")

    try:
        # 3. Pass the dynamic file path down to your background workers
        background_tasks.add_task(archive_pdf_to_drive, dynamic_pdf_path)
        background_tasks.add_task(log_to_google_sheet, payload.name, payload.email, payload.company, "Active Intake Initialized")
        background_tasks.add_task(send_outreach_email, payload.email, payload.company, dynamic_pdf_path)
        
        return {
            "status": "synchronized",
            "message": "Lead sequence processing initiated successfully."
        }
        
    except Exception as core_err:
        raise HTTPException(
            status_code=500,
            detail=f"Internal automation engine failure state mapping: {str(core_err)}"
        )

@app.get("/")
def health_check():
    return {"status": "healthy"}
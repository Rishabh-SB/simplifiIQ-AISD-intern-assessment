# SimplifiiQ (MOCK) Lead Engine and AI Automation Assessment Pipeline

An enterprise-grade asynchronous lead generation and AI automation assessment pipeline built for SimplifiiQ (MOCK). The system inputs user metadata via a corporate frontend interface, validates payload integrity via strict structural data layers, and kicks off isolated background worker tasks to process metrics, generate dynamic assessment reports, and dispatch custom client outreach material.

---

## System Architecture

The project is structured as a decoupled monorepo containing distinct, self-contained runtimes:

- `/frontend`: Built with Next.js 14 (App Router), TypeScript, and Tailwind CSS, styled to mirror the SimplifiiQ (MOCK) color framework.
- `/backend`: Engineered with FastAPI (Python), utilizing Pydantic validation barriers, exponential backoff resiliency loops for network operations, and multi-threaded background queues for heavy integrations.

---

## Quick Start Guide

### Prerequisites

Ensure you have the following package runtimes installed globally on your machine:

- Node.js (v18.0.0 or higher)
- Python (v3.10 or higher)

---

### 1. Backend Engine Provisioning

1. Navigate into the backend ecosystem directory:

   ```bash
   cd backend
   ```

2. Establish an isolated Python virtual environment container:

   ```bash
   python -m venv venv
   ```

3. Activate the newly created virtual sub-environment:

   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Mac/Linux: `source venv/bin/activate`

4. Install the required dependencies and integrations packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Initialize your environment variables template:

   ```bash
   cp .env.example .env
   ```

   Open the newly created local `.env` file and plug in your verified OAuth tokens, target spreadsheet/drive anchors, Resend keys, and your GEMINI_API_KEY infrastructure identifier.

6. Fire up the live reload Uvicorn server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

---

### 2. Frontend User Interface Initialization

1. Open a new terminal shell and navigate to the UI root folder:

   ```bash
   cd frontend
   ```

2. Install the cached dependencies cleanly via your package manager:

   ```bash
   npm install
   ```

3. Boot up the localized Next.js development server:

   ```bash
   npm run dev
   ```

4. Launch your web browser and view the responsive interface running live at: http://localhost:3000

---

## Production Resiliency and Validation Ecosystem

To mimic professional production environments, this pipeline implements critical safeguards to survive real-world edge cases:

- Pydantic Enforcement Barrier: The backend completely intercepts malformed payloads (e.g., blank strings or structural email syntax failures) at the gateway before wasting third-party API quotas.
- Exponential Backoff Retries: Network-bound pipelines interacting with Google Drive, Sheets, or Resend automatically catch network drops, rate limits (429), or upstream service degradation (5xx) and retry with a progressive wait delay multiplier.
- Asynchronous Background Workers: Long-running generation workflows are uncoupled from the HTTP response loop using FastAPI's native BackgroundTasks system, returning immediate feedback flags to the UI while processes run safely in the background.
- Dynamic Document Compiling: Local temporary PDF report files are cleanly namespaced on the file system utilizing sanitized variants of incoming company name strings rather than standard mock labels.

---

## Environment Variable Configuration Schema

Your local private .env files are strictly isolated from source control repositories via strict tree mapping exclusions inside our core .gitignore. Maintain the following parameters within your local configurations:

```env
# Google Developer Credentials
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REFRESH_TOKEN=your_refresh_token_here

# Target Cloud Infrastructure Anchors
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_SHEET_ID=your_sheet_id_here

# Resend Communication Gateway
RESEND_API_KEY=your_resend_key_here
FROM_EMAIL=onboarding@resend.dev

# Core Processing Models
GEMINI_API_KEY=your_gemini_api_key_here
```

# SimplifIQ Intel Engine: Automated Lead Enrichment Pipeline



https://github.com/user-attachments/assets/9d8a5aff-b759-4f22-b688-d2b5d9ed487e


Tracking google sheet: https://docs.google.com/spreadsheets/d/1wuZ-yS-neJaXnYnPQge4iL8msHrEfZ0dzlCeTnV322w
Tracking google drive folder: https://drive.google.com/drive/folders/1_lec1BYoj8bYcruVCII8jSC9MtQraHlb

This repository contains a production-ready, fully automated end-to-end lead ingestion and enrichment system built in response to the SimplifIQ AI Software Developer Intern Assessment.

When a prospect submits a lead intake form containing their company details, the system seamlessly takes over without any human intervention:

1. Captures and validates incoming lead data via strict type-safety checks.
2. Scrapes and enriches corporate profiles asynchronously from live target sources.
3. Leverages LLMs (gemini-2.5-flash) to generate structured domain-specific growth and automation recommendations.
4. Dynamically generates a highly polished, corporate-styled advisory PDF report.
5. Transmits the PDF directly to the user's inbox using automated email infrastructure.
6. Executes Bonus Trackers: Logs real-time metrics to a centralized Google Sheets CRM tracking framework and archives an unalterable copy of the PDF report inside a specific Google Drive folder.

---

## System Architecture

The project is structured as a completely decoupled monorepository housing two self-contained runtimes:

```text
├── frontend/             # Next.js 14 Web Application
│   ├── app/
│   │   ├── layout.tsx    # Global styles and provider context
│   │   └── page.tsx      # Main interactive Client Lead UI form
│   └── ...
└── backend/              # FastAPI Python Microservice
    ├── main.py           # API endpoints, middleware, background task queue
    ├── scraper.py        # Async httpx web scraper and Gemini 2.5 integration
    ├── reporter.py       # ReportLab PDF design and generation script
    ├── integrations.py   # Google Drive, Sheets, and Resend API conduits
    └── requirements.txt  # Python dependency list

```

---

## Prerequisites and Local Setup

### 1. External API Configuration and Credentials

To spin up this service off your own device, you will need to acquire credentials for the following services and populate your environment files.

#### A. Google Gemini API

- Visit Google AI Studio, generate a new API key, and save it. This powers the high-fidelity automated business analysis engine.

#### B. Resend API

- Create an account at Resend to obtain an API key for automated email delivery. If you haven't configured a custom sending domain, you can fallback to using Resend's default onboarding mailbox (onboarding@resend.dev).

#### C. Google Cloud Console (Drive and Sheets Automation)

To run the automated backup tracking assets, create a project in the Google Cloud Console:

1. Enable both the Google Sheets API and Google Drive API.
2. Configure your OAuth Consent Screen and create an OAuth 2.0 Client ID.
3. Secure your Client ID and Client Secret.
4. Generate a persistent Refresh Token via your app authentication handshake (ensuring scopes for drive.file and spreadsheets are requested).
5. Create a blank tracking sheet in Google Sheets and a folder in Google Drive, then extract their unique IDs from their browser URLs.

---

## Step-by-Step Installation

### Backend Setup (FastAPI)

1. Navigate into the backend subfolder:

```bash
cd backend

```

2. Create and activate a secure virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

```

3. Install all necessary upstream dependencies leveraging the bundled requirements file:

```bash
pip install -r requirements.txt

```

4. Create a .env file inside the root of your backend/ directory and populate it with your environment keys:

```env
# Core Config
GEMINI_API_KEY=your_gemini_api_key_here
RESEND_API_KEY=re_your_resend_api_key_here
FROM_EMAIL=onboarding@resend.dev

# Google API OAuth2 Configurations
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REFRESH_TOKEN=your_oauth2_refresh_token_here

# Tracking Framework Targets
GOOGLE_SHEET_ID=your_google_sheet_spreadsheet_id_here
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id_here

```

5. Launch your Uvicorn development server:

```bash
uvicorn main:app --reload --port 8000

```

_The backend engine will now be active at http://localhost:8000. You can review the auto-generated documentation schemas at http://localhost:8000/docs._

---

### Frontend Setup (Next.js)

1. Open a new terminal window and navigate into the frontend subfolder:

```bash
cd frontend

```

2. Install Node.js project packages:

```bash
npm install
# or
yarn install

```

3. Create a .env.local configuration layer inside the root of your frontend/ folder:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

```

4. Boot up the local web UI environment:

```bash
npm run dev
# or
yarn dev

```

_Open your browser and navigate to http://localhost:3000 to interact with the system._

---

## Verifying the End-to-End Workflow

1. Open the UI at http://localhost:3000.
2. Enter your credentials along with any target operational business web domain into the intake form.
3. Submit the form. The UI will instantly display a loading sequence while sending a request to the FastAPI application.
4. FastAPI handles the incoming validation barrier instantly. It passes the task over to a multi-threaded Background Queue, letting the frontend know the request was accepted right away so the user doesn't experience timeouts.
5. Watch your terminal logs to observe the system working in the background:

- Scraping: Fetches live content from the target homepage using httpx and parses it with BeautifulSoup (with graceful fallback handling for anti-scraping blocks).
- Enriching: Feeds the cleaned context to gemini-2.5-flash to extract an executive corporate profile and custom strategy matrices.
- Reporting: Compiles a clean, executive-styled corporate PDF report.
- Integrating and Archiving: Uploads the file to Google Drive, logs operational rows to Google Sheets, and sends out the email via Resend.

6. Check your recipient inbox—a tailored advisory audit PDF will be waiting for you, and your Google Drive folder and Sheets tracker will reflect the new entry instantly.

---

## Architectural Decisions and Resiliency Fallbacks

- Non-Blocking Background Tasks: Heavy scraping, PDF generation, and multi-network API connections occur fully outside the core request-response lifecycle inside FastAPI's BackgroundTasks queue, keeping the frontend client snappy and highly responsive.
- Scraping Protection Barriers: If a target domain blocks standard HTTP requests or times out, the scraping module safely logs a warning and yields a structured layout to Gemini, which infers core business models from known domain structures.
- Automated Session Handshakes: Google API authentication credentials utilize automatic underlying token transport refresh handlers to eliminate session expiration bugs midway through high-volume data loops.
- Disk Cleanliness: The pipeline enforces a strict execution sequence that cleans up files locally right after processing, ensuring no orphaned PDFs take up server space.

# AI Webpage Monitor

A smart, AI-powered webpage monitoring tool that detects new content, extracts insights, and sends daily summaries via email. Powered by Google Gemini and Playwright.

## Features

- **Smart Detection**: Uses diffing algorithms to detect significant content changes.
- **AI Summarization**: Uses Google Gemini (via `google-generativeai`) to generate concise, insightful summaries of new content.
- **Link Extraction**: Automatically finds and links to the specific source articles.
- **Daily Reports**: Sends a consolidated email report with summaries and key insights. Even if no new content is found, a "No New Content" confirmation email is sent to ensure the monitor is active.
- **Anti-Bot Bypass**: Includes basic logic to handle Cloudflare visuals/challenges using Playwright. (Enhanced with automation checks).

## Prerequisites

- Python 3.10+
- Google Cloud API Key (for Gemini)
- Gmail Account (for sending reports)

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/henryhyunwookim/webpage-monitor.git
    cd webpage-monitor
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  **Environment Variables**:
    Create a `.env` file based on `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Fill in your API keys:
    - `GOOGLE_API_KEY`: Your Gemini API Key.
    - `SMTP_PASSWORD`: Your Gmail App Password (not your login password).

4.  **Configuration**:
    Create a `config.yaml` based on `config.example.yaml`:
    ```bash
    cp config.example.yaml config.yaml
    ```
    Edit `config.yaml` to list the websites you want to monitor:
    ```yaml
    sites:
      - url: "https://example.com/blog"
        name: "Example Blog"
    ```

## Usage

**Run the monitor manually**:
```bash
python main.py
```

**First Run**:
On the first run, the tool will fetch the current state of all pages and summarize the *most recent* post found on each page to establish a baseline.

**Daily Automation**:
You can use `cron` (Linux) or Task Scheduler (Windows) to run `main.py` once a day.

### Cloud Deployment (Google Cloud Run)

This repository includes a deployment script (`deploy.ps1`) to automate deployment to Google Cloud Run (Free Tier).

**Prerequisites**:
- Google Cloud Project with billing enabled.
- `gcloud` CLI installed and authenticated.
- Required APIs enabled: `run.googleapis.com`, `cloudbuild.googleapis.com`, `scheduler.googleapis.com`, `storage.googleapis.com`.

**Steps**:
1.  **Configure `deploy.ps1`**:
    Edit the top variables in `deploy.ps1` to match your GCP project ID and region.
    ```powershell
    $PROJECT_ID = "your-project-id"
    ```

2.  **Run Deployment**:
    ```powershell
    .\deploy.ps1
    ```
    This will:
    -   Create a GCS bucket for history storage.
    -   Build and push the Docker image.
    -   Deploy/Update the Cloud Run Job.
    -   Create/Update the Cloud Scheduler Job (Schedule: Daily at Midnight KST).

3.  **Set Environment Variables**:
    Go to the Google Cloud Run Console > Jobs > `webpage-monitor-job` > Edit > Variables & Secrets.
    Add:
    -   `GOOGLE_API_KEY`
    -   `SMTP_PASSWORD`

4.  **Update Config**:
    Ensure your `config.yaml` points to the created GCS bucket:
    ```yaml
    storage_file: "gs://your-project-id-monitor-data/history.json"
    ```

## License
Creative Commons Attribution-NonCommercial 4.0 International License.
See [LICENSE](LICENSE) file for details.

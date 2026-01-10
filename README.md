# AI Webpage Monitor

A smart, AI-powered webpage monitoring tool that detects new content, extracts insights, and sends daily summaries via email. Powered by Google Gemini and Playwright.

## Features

- **Smart Detection**: Uses diffing algorithms to detect significant content changes.
- **AI Summarization**: Uses Google Gemini (via `google-generativeai`) to generate concise, insightful summaries of new content.
- **Link Extraction**: Automatically finds and links to the specific source articles.
- **Daily Reports**: Sends a consolidated email report with summaries and key insights.
- **Anti-Bot Bypass**: Includes basic logic to handle Cloudflare visuals/challenges using Playwright.

## Prerequisites

- Python 3.10+
- Google Cloud API Key (for Gemini)
- Gmail Account (for sending reports)

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/webpage-monitor.git
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

### Cloud Deployment (Optional)
This project is ready for Google Cloud Run. See `implementation_plan.md` (if available) or standard Cloud Run docs for deploying a Python script as a job.

## License
MIT

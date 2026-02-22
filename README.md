# AI Webpage Monitor

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-v1.40+-green.svg)](https://playwright.dev/)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange.svg)](https://deepmind.google/technologies/gemini/)

A professional, AI-native webpage monitoring engine designed to track updates, summarize changes with high precision, and deliver actionable insights directly to your inbox. Optimized for both local use and cloud-native deployment on Google Cloud Platform.

---

## 🏗️ Architecture & System Design

The application follows a modular architecture based on a **Fetch-Extract-Diff-Summarize-Notify** pipeline. This design ensures separation of concerns, allowing for easy updates to the AI model, fetching logic, or storage backend.

### System Overview

Standard flow of the monitoring engine:

```text
[ config.yaml ]       [ .env ]
       |                 |
       v                 v
    +-----------------------+
    |       src/main.py     | (Orchestrator)
    +-----------+-----------+
                |
    +-----------v-----------+      +-----------------------+
    |       Fetcher         | ---> |   Target Webpages     |
    | (Playwright/Stealth)  |      | (Bypass Anti-Bot)     |
    +-----------+-----------+      +-----------------------+
                |
    +-----------v-----------+      +-----------------------+
    |     Diff Engine       | <--- |    Storage Backend    |
    | (Set-based comparison)|      | (Local JSON / GCS)    |
    +-----------+-----------+      +-----------------------+
                |
    +-----------v-----------+      +-----------------------+
    |      Summarizer       | ---> |   Google Gemini AI    |
    | (Insight Extraction)  |      |   (LMM Analysis)      |
    +-----------+-----------+      +-----------------------+
                |
    +-----------v-----------+      +-----------------------+
    |       Notifier        | ---> |    User's Inbox       |
    |  (SMTP / Gmail API)   |      | (Daily Report / MD)   |
    +-----------------------+      +-----------------------+
```

> [!NOTE]
> If your viewer supports Mermaid, you will see a dynamic version of the diagram below.

```mermaid
graph TD
    M["src/main.py"] --> F["Fetcher"]
    M --> S["Storage"]
    M --> D["Diff Engine"]
    M --> AI["Summarizer"]
    M --> N["Notifier"]

    C["config.yaml"] --> M
    E[".env"] --> M
    
    F --> WEB["Target Webpages"]
    AI --> SUM["Gemini AI"]
    N --> EMAIL["User Inbox"]
```

### 📁 Repository Structure

The project follows a clean, modular structure:

```text
.
├── config/               # Configuration templates
│   ├── .env              # Environment variables
│   └── config.yaml       # Active site configuration
├── deploy/               # Deployment manifests
│   ├── .gcloudignore     # Google Cloud ignore file
│   ├── deploy.ps1        # Deployment script
│   └── Dockerfile        # Dockerfile
├── scripts/              # Utility scripts for local execution
│   └── run.bat           # Run script
├── src/                  # Application source code
│   ├── monitor/          # Pipeline logic
│   │   ├── diff.py       # Diff logic
│   │   ├── fetcher.py    # Fetcher logic
│   │   ├── notifier.py   # Notifier logic
│   │   ├── stealth.py    # Stealth layer logic
│   │   ├── storage.py    # Storage logic
│   │   └── summarizer.py # Summarizer logic
│   └── main.py           # Main entry point
├── .gitignore            # Git ignore file
├── LICENSE               # License file
├── README.md             # Documentation
└── requirements.txt      # Python dependencies
```

---

## 🧠 Generalizability & Intelligence

This monitor is designed to be **platform-agnostic** and can be used to track updates on virtually any website. Unlike traditional CSS-selector based tools, it leverages:

### 1. Browser-Based Extraction (Playwright)
By using a real Chromium browser, the monitor can handle:
- **Single Page Applications (SPAs)**: Even if content is loaded dynamically via JavaScript (React, Vue, etc.), the monitor sees exactly what a user sees.
- **Anti-Bot Stealth**: Built-in layers to bypass Cloudflare and other automated traffic blockers.

### 2. LLM-Powered Semantic Analysis
Instead of looking for specific HTML tags that might change during a site site redesign, the monitor:
- Extracts the **raw text content** of the page.
- Uses **Google Gemini** to "read" and understand the changes.
- Summarizes only relevant updates, filtering out noise like layout shifts or ads.

### 3. Stateful set-based Diffing
The engine compares content line-by-line, making it extremely resilient to site redesigns while remaining sensitive to new informative text.

### Logical Flow
1.  **Configuration Loading**: Orchestrates the cycle based on `config.yaml` and environment variables.
2.  **Intelligent Fetching**: Launches a headless browser instance per site using **Playwright**, applying a sophisticated **Stealth Layer** to bypass automated traffic blockers (Cloudflare, etc.).
3.  **Content Extraction**: Parses the DOM using BeautifulSoup, striping noise (nav, footer, scripts) while preserving Markdown-style links for AI context.
4.  **Stateful Diffing**: Compares current content against historical data stored in the **Storage Backend**. It uses a set-based line comparison to identify unique *added* content while ignoring minor layout shifts.
5.  **AI Analysis**: Sends the "new content" to **Google Gemini**. The system uses specialized prompt engineering to:
    - Identify specific article titles and source URLs.
    - Synthesize a "So What?" focused summary.
    - Extract key strategic insights.
6.  **Reporting**: Aggregates all site updates into a single Markdown-formatted email. Supports a "No New Content" heartbeat to confirm system health.

---

## 🚀 Key Functionalities

### 🧠 AI-Powered Insights
Unlike traditional monitors that only detect change, this tool *understands* the change. Using Gemini 1.5 Flash, it filters out noise and summarizes long updates into concise, bulleted insights.

### 🕵️ Advanced Stealth & Anti-Bot
Built-in protection against modern bot-detection:
- **Playwright Stealh**: Overrides `navigator.webdriver`, mocks `chrome` objects, and mimics real-user plugins/MimeTypes.
- **Human-like Interaction**: Randomized timeouts and specific user-agent rotations.
- **State Persistence**: Saves browser state (cookies/tokens) after successfully bypassing challenges to ensure smoother subsequent runs.

### ☁️ Cloud-Native Storage
Seamlessly switch between:
- **LocalStorage**: Perfect for single-machine usage.
- **GCSStorage**: Enterprise-ready storage using Google Cloud Storage, enabling serverless execution on Cloud Run.

---

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.10+**
- **Google Cloud API Key** (for Gemini)
- **Gmail Account** (for sending reports)

### 1. Installation
```bash
git clone https://github.com/henryhyunwookim/webpage-monitor.git
cd webpage-monitor
pip install -r requirements.txt
playwright install chromium
```

### 2. Configuration
Create a `.env` file:
```bash
GOOGLE_API_KEY=your_gemini_key
SMTP_PASSWORD=your_gmail_app_password
```

### 3. Execution

Run the monitor locally:
```bash
# Using the Windows runner
./scripts/run.bat

# Or directly via Python
python src/main.py
```

Run using Docker:
```bash
docker build -t webpage-monitor -f deploy/Dockerfile .
docker run --env-file .env webpage-monitor
```

---

## ☁️ Deployment (Google Cloud Run)

The repository includes a `deploy/deploy.ps1` script for one-command deployment to GCP.

### Automated Cloud Architecture
- **Cloud Run Job**: Executes the monitoring logic containerized.
- **Cloud Scheduler**: Triggers the job daily (or on your preferred schedule).
- **GCS Bucket**: Persists the monitoring history across serverless executions.

To deploy:
1. Update `$PROJECT_ID` in `deploy/deploy.ps1`.
2. Run `pwsh deploy/deploy.ps1` in PowerShell.

---

## 📜 License
Creative Commons Attribution-NonCommercial 4.0 International License.
See [LICENSE](LICENSE) file for details.

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only to save space)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .
# Ensure config file is in expected location
COPY config/config.yaml config/config.yaml

# Entrypoint
CMD ["python", "src/main.py"]

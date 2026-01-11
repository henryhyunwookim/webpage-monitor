import yaml
import os
import argparse
import logging
from dotenv import load_dotenv
from monitor.storage import Storage
from monitor.fetcher import Fetcher
from monitor.diff import get_new_content
from monitor.summarizer import Summarizer
from monitor.notifier import Notifier
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("monitor.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def load_config(path='config.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    load_dotenv() # Load env vars from .env
    
    parser = argparse.ArgumentParser(description="Webpage Monitor")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)
    
    storage = Storage(config['storage_file'])
    fetcher = Fetcher()
    summarizer = Summarizer(model_name=config['llm']['model'])
    notifier = Notifier(config['email'])
    
    report_items = []
    
    logger.info("Starting monitoring cycle...")
    
    for site in config['sites']:
        url = site['url']
        name = site['name']
        logger.info(f"Checking {name} ({url})...")
        
        # 1. Fetch
        full_html = fetcher.fetch(url)
        if not full_html:
            logger.warning(f"Failed to fetch content for {url}")
            continue
            
        # 2. Extract Text
        if site.get('type') == 'video':
            # For video pages, we might want both or specifically metadata
            text_content = fetcher.extract_video_metadata(full_html) + "\n" + fetcher.extract_text(full_html)
        else:
            text_content = fetcher.extract_text(full_html)
            
        # 3. Get Previous State
        site_data = storage.get_site_data(url)
        last_content = site_data.get('last_content', "")
        
        # 4. Diff
        new_content = get_new_content(last_content, text_content)
        
        # 5. Check First Run or Threshold
        if not last_content:
             # First run initialization
            logger.info(f"First run for {name}. Identify the most recent post.")
            
            initial_summary = summarizer.summarize(
                text_content, 
                context={
                    "name": name, 
                    "url": url,
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "is_first_run": True
                }
            )
            
            report_items.append({
                "name": name,
                "url": url,
                "new_content_snippet": "Initial Run - Latest Post Extraction",
                "summary": initial_summary
            })
            
            storage.update_site_data(url, text_content)
            continue

        threshold = config.get('diff_threshold', 10)
        if len(new_content) < threshold:
            logger.info(f"No significant changes for {name}.")
            # Even if no change, we might want to update storage if we want to track 'last seen' as now,
            # but usually we only update if content changed or if we want to effectively 'mark as read'.
            # If we don't update key, next run will still see it as new? 
            # Actually, fetcher fetches current state. If we don't update storage, next time fetcher gets same content, 
            # comparison against old storage -> same diff.
            # So, we SHOULD update storage regardless, effectively "acknowledging" the current state.
            # OPTION A: Always update to validation state.
            # OPTION B: Only update if changed.
            # Use Option A to avoid re-alerting on same content if we just missed the threshold but it was a little change.
            if not last_content: 
                # Should not be reached due to above check, but keeping clean cleanup if needed
                pass
            continue
            
        logger.info(f"Detected {len(new_content)} chars of new content.")
        
        # 6. Summarize
        current_date_str = datetime.now().strftime("%B %d, %Y") # e.g., January 07, 2026
        summary = summarizer.summarize(
            new_content, 
            context={
                "name": name, 
                "url": url,
                "date": current_date_str
            }
        )
        
        # 7. Add to Report
        report_items.append({
            "name": name,
            "url": url,
            "new_content_snippet": new_content[:200].replace("\n", " "),
            "summary": summary
        })
        
        # 8. Update Storage
        storage.update_site_data(url, text_content)
        
    # 9. Send Report
    date_str = datetime.now().strftime("%Y-%m-%d")
    if report_items:
        report_lines = [f"# Daily Monitor Report - {date_str}\n"]
        
        for item in report_items:
            report_lines.append(f"## {item['name']}")
            report_lines.append(f"**URL**: {item['url']}\n")
            report_lines.append(f"### Summary")
            report_lines.append(f"{item['summary']}\n")
            report_lines.append(f"---")
            
        report_markdown = "\n".join(report_lines)
        subject = f"Webpage Monitor Report - {date_str}"
        logger.info("Sending email report...")
    else:
        logger.info("No new content detected across all sites.")
        report_markdown = f"# Daily Monitor Report - {date_str}\n\nNo new content was detected across all monitored sites today."
        subject = f"Webpage Monitor: No New Content - {date_str}"
        logger.info("Sending 'No Content' email notification...")

    notifier.send_report(subject, report_markdown)
    
    # Also save locally
    os.makedirs("data", exist_ok=True)
    with open(f"data/report_{date_str}.md", "w", encoding="utf-8") as f:
        f.write(report_markdown)

if __name__ == "__main__":
    main()

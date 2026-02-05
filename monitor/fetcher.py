from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import SCRIPTS
from bs4 import BeautifulSoup
import logging
import os

logger = logging.getLogger(__name__)

class Fetcher:
    def __init__(self):
        # Playwright context is managed per fetch for simplicity in this script, 
        # or we could keep a browser instance open if we refactor main.py.
        # For now, let's open/close per request for safety and preventing leaks in simple script.
        pass

    def fetch(self, url: str) -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled", 
                        "--start-maximized", 
                        "--disable-infobars"
                    ],
                    ignore_default_args=["--enable-automation"]
                )
                
                # Check for storage state
                state_file = "state.json"
                context_args = {
                    "user_agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                    "viewport": {'width': 1920, 'height': 1080},
                    "locale": 'en-US',
                    "timezone_id": 'America/New_York'
                }
                
                if os.path.exists(state_file):
                    logger.info("Loading browser state from state.json...")
                    context_args["storage_state"] = state_file

                context = browser.new_context(**context_args)
                
                page = context.new_page()
                
                # Apply stealth manually since stealth_sync is missing
                for script in SCRIPTS.values():
                    context.add_init_script(script)

                logger.info(f"Navigating to {url} with Playwright...")
                # Increase timeout to 60s
                page.goto(url, timeout=60000)
                
                # Wait for some content to load.
                try:
                    # Cloudflare challenge often takes 5-10s.
                    page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass

                # Check if we are on challenge page (robust check)
                content_str = page.content().lower()
                title_str = page.title().lower()
                
                if any(x in title_str for x in ["just a moment", "verify you are human", "cloudflare", "しばらくお待ちください"]) or "verify you are human" in content_str:
                    logger.info("Challenge page detected. Waiting for stealth bypass...")
                    
                    # Even with stealth, sometimes a little wait helps scripts run
                    page.wait_for_timeout(5000)
                    
                    # Re-check
                    content_str = page.content().lower()
                    if "verify you are human" in content_str:
                         logger.info("Still on challenge page. Waiting longer...")
                         page.wait_for_timeout(10000)
                
                content = page.content()
                
                # Save state if possible (to capture cookies/tokens after bypass)
                if "verify you are human" not in content.lower():
                     context.storage_state(path=state_file)
                     
                browser.close()
                return content
        except Exception as e:
            logger.error(f"Error fetching {url} with Playwright: {e}")
            return ""

    def extract_text(self, html: str, site_config: dict = None) -> str:
        if not html:
            return ""
        
        soup = BeautifulSoup(html, 'html.parser')

        # Security/Challenge Page Detection
        # Cloudflare and others often have specific titles or text
        text_lower = soup.get_text().lower()
        if any(x in text_lower for x in ["verify you are human", "just a moment...", "cloudflare", "しばらくお待ちください"]):
            logger.warning("Detected security challenge page. Skipping content extraction to avoid false positives.")
            return ""
        
        # Remove scripts, styles, and other noise
        for script in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"]):
            script.decompose()

        # Custom text extraction to preserve links
        # 1. Replace <a> tags with Markdown link format
        for a in soup.find_all('a', href=True):
            link_text = a.get_text(strip=True)
            href = a['href']
            # Resolve relative URLs if needed, but for now assuming base or just preserving text
            # If href starts with /, prepend site url if we had it, but here we just have html.
            # We can leave it as relative or try to be smart. Let's just keep it as is.
            if link_text:
                new_tag = soup.new_tag("span")
                new_tag.string = f"[{link_text}]({href})"
                a.replace_with(new_tag)

        # Specific handling based on site config 'type' or url patterns could go here
        # For general text:
        text = soup.get_text(separator='\n')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

    def extract_video_metadata(self, html: str) -> str:
        """Helper for video pages to get meta descriptions/titles if text is sparse."""
        soup = BeautifulSoup(html, 'html.parser')
        content = []
        
        # Try to find OG tags which often have good summaries
        for tag in soup.find_all("meta"):
            if tag.get("property", "").startswith("og:") or tag.get("name", "").startswith("twitter:"):
                 if tag.get("property") in ["og:title", "og:description"] or tag.get("name") in ["twitter:title", "twitter:description"]:
                     content.append(f"{tag.get('property') or tag.get('name')}: {tag.get('content')}")

        return "\n".join(content)

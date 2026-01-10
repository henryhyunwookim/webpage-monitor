import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash"):
        # Configure API key
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            logger.warning("No Google API Key found. Summarization will be skipped or fail.")
        else:
            genai.configure(api_key=key)
            self.model = genai.GenerativeModel(model_name)

    def summarize(self, text: str, context: dict) -> str:
        if not text or len(text) < 50:
            return "No significant new content to summarize."
        
        try:
            is_first_run = context.get('is_first_run', False)
            
            # Unified format instructions
            format_instructions = """
            OUTPUT FORMAT (Strict Markdown):
            **Title**: <Extracted Title of the Article>
            **Date**: <Extracted Date or "Unknown">
            **Source**: <Specific Article URL found in text, NOT the main page URL>
            **Summary**:
            <Provide a rich, descriptive summary here. Focus on the "So What?". Why is this important? What are the key details?>
            **Key Insights**:
            - <Insight 1>
            - <Insight 2>
            """

            if is_first_run:
                task_instruction = f"""
                TASK (INITIAL RUN): 
                1. Identify the SINGLE most recent news article, blog post, or update from the text.
                2. The text contains links in `[text](url)` format. FIND the specific URL for this article.
                   - If the link is relative (e.g. `/article`), prepend the main site URL: {context.get('url', '').rstrip('/')}
                3. Key criterion: It should be the item that appears to be the latest addition to the page.
                4. DO NOT filter for "Today's Date". Summarize the absolute latest post.
                5. Provide a detailed, insightful summary.
                
                {format_instructions}
                """
            else:
                task_instruction = f"""
                TASK (MONITORING):
                1. Identify any news, articles, or posts explicitly dated "Today" or "{context.get('date', 'Unknown')}".
                2. If no dates are present, assume the new text is relevant.
                3. The text contains links in `[text](url)` format. FIND the specific URL for these items.
                4. Provide a detailed, insightful summary for each item found.
                
                {format_instructions}
                """

            prompt = f"""
            You are a highly analytical news monitoring assistant.
            Today's Date: {context.get('date', 'Unknown')}
            
            I am analyzing the webpage: {context.get('name', 'Unknown')} ({context.get('url', 'Unknown')}).
            
            Text Content (Markdown links included):
            \"\"\"
            {text[:20000]} 
            \"\"\"
            
            {task_instruction}
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            return f"Error generating summary: {e}"

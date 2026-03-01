import logging
import os
import sys

def setup_logging(default_level=logging.INFO):
    """
    Sets up consistent logging for the application.
    In Cloud Run: Logs to stdout only.
    Locally: Logs to stdout and a file in logs/monitor.log.
    """
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Detect Cloud Run environment
    is_cloud_run = os.environ.get('K_SERVICE') or os.environ.get('CLOUD_RUN_JOB')
    
    if not is_cloud_run:
        try:
            # Determine path to logs directory (relative to this file)
            # This file is in src/monitor/logger.py
            # So dirname(__file__) is src/monitor
            # .. is src, .. is root
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            log_dir = os.path.join(base_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "monitor.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            handlers.append(file_handler)
        except Exception as e:
            # Fallback to console only if file logging fails
            print(f"Warning: Failed to initialize file logging: {e}", file=sys.stderr)

    # Configure root logger
    logging.basicConfig(
        level=default_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    # Create a wrapper logger to return if needed, but basicConfig handles it globally
    return logging.getLogger()

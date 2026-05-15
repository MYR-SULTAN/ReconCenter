import webview
import os
import sys
import logging
from pathlib import Path

from backend.api import Api
from backend.storage.db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Cyber Recon Command Center...")
    
    # Initialize DB
    init_db()
    
    # Setup API bridge
    api = Api()
    
    # Resolve frontend path
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_dir = Path(sys._MEIPASS)
    else:
        # Running normally
        base_dir = Path(__file__).parent
        
    frontend_dir = base_dir / "frontend"
    entry_html = frontend_dir / "index.html"
    
    if not entry_html.exists():
        logger.error(f"Frontend entry point not found at {entry_html}")
        sys.exit(1)

    # Create window
    window = webview.create_window(
        'Cyber Recon Command Center', 
        url=f'file://{entry_html.absolute()}',
        js_api=api,
        width=1280,
        height=800,
        min_size=(1024, 768),
        background_color='#0f1115' # Dark background to match theme
    )
    
    api.set_window(window)
    
    # Start webview loop
    logger.info("Starting window...")
    webview.start(debug=True)

if __name__ == '__main__':
    main()

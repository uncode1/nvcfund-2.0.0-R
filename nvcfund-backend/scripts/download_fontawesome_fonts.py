#!/usr/bin/env python3
"""
FontAwesome Font Downloader
Downloads FontAwesome 6.4.0 webfont files locally for offline use
"""

import os
import requests
from pathlib import Path

def download_fontawesome_fonts():
    """Download FontAwesome webfont files"""
    
    # Base URL for FontAwesome 6.4.0 webfonts
    base_url = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/"
    
    # Font files to download
    font_files = [
        "fa-solid-900.woff2",
        "fa-solid-900.woff",
        "fa-solid-900.ttf",
        "fa-regular-400.woff2", 
        "fa-regular-400.woff",
        "fa-regular-400.ttf",
        "fa-brands-400.woff2",
        "fa-brands-400.woff", 
        "fa-brands-400.ttf"
    ]
    
    # Create webfonts directory
    webfonts_dir = Path("../static/icons/fontawesome/webfonts")
    webfonts_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading FontAwesome webfont files...")
    
    for font_file in font_files:
        url = base_url + font_file
        local_path = webfonts_dir / font_file
        
        try:
            print(f"Downloading {font_file}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
                
            print(f"✓ Downloaded {font_file} ({len(response.content)} bytes)")
            
        except Exception as e:
            print(f"✗ Failed to download {font_file}: {e}")
    
    print("\nFontAwesome font download complete!")
    print(f"Files saved to: {webfonts_dir.absolute()}")

if __name__ == "__main__":
    download_fontawesome_fonts()

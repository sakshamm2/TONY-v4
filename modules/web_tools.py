"""
Module   : modules.web_tools
Project  : T.O.N.Y. v4
Purpose  : Core Engine for Network Requests, API Interaction, and Web Scraping
"""

from __future__ import annotations
import os
import json
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# Optional dependencies for web scraping and network requests
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None
    print("[SYSTEM WARNING] 'requests' or 'beautifulsoup4' not installed. Web tools disabled.")


class WebManager:
    """
    Handles robust external network interactions, HTML parsing, and secure file downloads.
    """
    # Standard headers to prevent basic bot-blocking from modern web servers
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # ==========================================================
    # Validation & Utilities
    # ==========================================================
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validates standard URL formatting before attempting network execution."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    # ==========================================================
    # API & JSON Interactions
    # ==========================================================
    @classmethod
    def fetch_json(cls, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a secure GET request expecting a JSON payload response.
        Useful for weather APIs, news feeds, and structured data queries.
        """
        if not requests:
            return {"success": False, "error": "Missing 'requests' dependency."}
            
        if not cls._is_valid_url(url):
            return {"success": False, "error": f"Invalid URL structure: {url}"}

        try:
            response = requests.get(
                url, 
                params=params, 
                headers=cls.DEFAULT_HEADERS, 
                timeout=10
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json()
            }
            
        except requests.exceptions.RequestException as req_err:
            return {"success": False, "error": str(req_err)}
        except json.JSONDecodeError:
            return {"success": False, "error": "Failed to decode JSON response from server."}

    # ==========================================================
    # Web Scraping & HTML Extraction
    # ==========================================================
    @classmethod
    def extract_text(cls, url: str) -> Dict[str, Any]:
        """
        Downloads a webpage and strips all HTML tags to return clean, readable text.
        Ideal for feeding context into the AI LLM.
        """
        if not requests or not BeautifulSoup:
            return {"success": False, "error": "Missing web scraping dependencies."}

        if not cls._is_valid_url(url):
            return {"success": False, "error": f"Invalid URL structure: {url}"}

        try:
            response = requests.get(url, headers=cls.DEFAULT_HEADERS, timeout=15)
            response.raise_for_status()

            # Parse HTML and extract raw text
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style elements which clutter the text output
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            text = soup.get_text(separator="\n", strip=True)
            
            return {
                "success": True,
                "title": soup.title.string if soup.title else "Unknown Title",
                "text_content": text
            }

        except Exception as e:
            return {"success": False, "error": f"Scraping failed: {e}"}

    # ==========================================================
    # Asset Management
    # ==========================================================
    @classmethod
    def download_file(cls, url: str, destination_dir: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Streams binary data from a URL directly to the local filesystem safely.
        """
        if not requests:
            return {"success": False, "error": "Missing 'requests' dependency."}

        if not cls._is_valid_url(url):
            return {"success": False, "error": f"Invalid URL structure: {url}"}

        try:
            os.makedirs(destination_dir, exist_ok=True)
            
            if not filename:
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    filename = "downloaded_file.dat"
                    
            filepath = os.path.join(destination_dir, filename)

            with requests.get(url, headers=cls.DEFAULT_HEADERS, stream=True, timeout=30) as response:
                response.raise_for_status()
                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

            return {
                "success": True, 
                "filepath": filepath,
                "message": f"Successfully downloaded to {filepath}"
            }

        except Exception as e:
            return {"success": False, "error": f"Download failed: {e}"}
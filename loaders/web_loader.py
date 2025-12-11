# loaders/web_loader.py
from urllib.parse import urlparse
import requests

def validate_txt_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and url.strip().lower().endswith(".txt")
    except Exception:
        return False

def fetch_text_from_url(url: str, timeout: int = 10) -> str:
    """
    Fetch raw text content from a URL. Raises requests.HTTPError on non-200.
    """
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text

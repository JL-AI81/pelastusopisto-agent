"""Työkalut agentille"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from config import ALLOWED_DOMAINS, MAX_CONTENT_LENGTH


def fetch_page(url):
    """
    Hae pelastusopisto.fi-sivu.
    
    Args:
        url (str): Sivun URL
        
    Returns:
        dict: {"status": "ok"/"error", "content": str}
    """
    # Tarkista domain
    parsed = urlparse(url)
    domain = parsed.netloc
    
    if domain not in ALLOWED_DOMAINS:
        return {
            "status": "error",
            "content": f"Virhe: Vain {ALLOWED_DOMAINS} sallittu. Annoit: {url}"
        }
    
    # Hae sivu
    try:
        headers = {
            'User-Agent': 'PelastusopistoAgent/1.0 (Educational purposes)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {
            "status": "error",
            "content": f"Virhe sivun haussa: {str(e)}"
        }
    
    # Parsii HTML
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Poista turhat tagit
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # Hae teksti
        text = soup.get_text(separator='\n', strip=True)
        
        # Rajaa pituus
        if len(text) > MAX_CONTENT_LENGTH:
            text = text[:MAX_CONTENT_LENGTH] + "\n\n[...sisältö katkaistu...]"
        
        return {
            "status": "ok",
            "content": text
        }
        
    except Exception as e:
        return {
            "status": "error",
            "content": f"Virhe parsinnassa: {str(e)}"
        }


# Tool schema OpenAI-muodossa
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": "Hae pelastusopisto.fi-sivun sisältö",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Sivun URL (pelastusopisto.fi)"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

# Työkalufunktioiden mappaus
TOOL_FUNCTIONS = {
    "fetch_page": fetch_page
}
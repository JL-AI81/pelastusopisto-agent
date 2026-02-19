"""Asetukset"""

import os

# Hae ympäristömuuttujasta (Streamlit Cloud)
# TAI käytä paikallista arvoa kun testaat
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "LAITA_TÄHÄN_PAIKALLISESTI")

MODEL = "llama-3.3-70b-versatile"
ALLOWED_DOMAINS = ["pelastusopisto.fi", "www.pelastusopisto.fi"]
MAX_CONTENT_LENGTH = 5000
import unicodedata
import re

def normalize(text: str | None) -> str:
    if not text:
        return ""
    
    # Remove accents
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.upper().strip()
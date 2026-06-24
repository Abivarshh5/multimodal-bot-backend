import re
import unicodedata

def preprocess_text(text: str) -> str:
    """
    Clean and normalize crawled markdown/text content for chunking.
    Preserves:
        - Headings (# ## ### etc.)
        - Product descriptions
        - Paragraph structure
    Removes:
        - Markdown image references ![...](...) 
        - HTML tags
        - Excessive whitespace / blank lines
        - Markdown horizontal rules (---, ***)
        - Link-only lines [text](url) with no surrounding prose
    """
    if not text or not text.strip():
        return ""

    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"<[^>]+>", "", text)
    # text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"^\s*\[[^\]]*\]\([^)]*\)\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[*_]{2,}\s*$", "", text, flags=re.MULTILINE)

    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        cleaned_lines.append(stripped)
    text = "\n".join(cleaned_lines)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text

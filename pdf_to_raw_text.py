# pdf_to_raw_text.py
import os
from pypdf import PdfReader

def get_text_from_pdf(file_path):
    """Extracts raw text from a PDF file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def get_text_from_md(file_path):
    """Extracts raw text from a Markdown file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading MD: {e}")
        return ""

def extract_text(file_path):
    """Auto-detects file type and gets text."""
    if file_path.endswith(".pdf"):
        return get_text_from_pdf(file_path)
    elif file_path.endswith(".md"):
        return get_text_from_md(file_path)
    else:
        return "Unsupported file format. Use .pdf or .md"
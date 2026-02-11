import os
from pypdf import PdfReader
from docx import Document


def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"

    return text.strip()


def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs]).strip()


def read_txt(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def extract_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return read_pdf(path)

    elif ext == ".docx":
        return read_docx(path)

    elif ext == ".txt":
        return read_txt(path)

    else:
        return read_txt(path)

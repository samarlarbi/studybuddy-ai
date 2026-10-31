from dataclasses import dataclass
from fastapi import HTTPException   # was: from http.client import HTTPException
from io import BytesIO

from pypdf import PdfReader


@dataclass
class Chunk:
    page: int
    index: int
    text: str


def chunk_text(text: str, size: int = 800, overlap: int = 150) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = text.rfind(" ", start, end)  # avoid cutting a word in half
            if cut > start + size // 2:
                end = cut
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        next_start = max(end - overlap, start + 1)
        if text[next_start - 1] != " ":
            # move forward to the next word boundary (never past `end`)
            space = text.find(" ", next_start, end)
            if space != -1:
                next_start = space + 1
        start = next_start
    return [c for c in chunks if c]

def extract_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    """Return [(page_number, text)] for pages that contain text."""
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((number, text))
    return pages


def chunk_pages(    pdf_bytes: bytes,    size: int = 800, overlap: int = 150):
    try:
        pages=extract_pages(pdf_bytes)
    except Exception:
        raise HTTPException(400, "Could not read this PDF")
    if not pages:
        raise HTTPException(422, "No text found. Scanned PDFs are not supported yet")

    chunks = []
    for page_number, text in pages:
        for piece in chunk_text(text, size, overlap):
            chunks.append(Chunk(page=page_number, index=len(chunks), text=piece))
    
    return chunks
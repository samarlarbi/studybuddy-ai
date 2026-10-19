from dataclasses import asdict

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.chunking import chunk_pages, extract_pages

app = FastAPI(title="Study Assistant AI")

MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB


class AskRequest(BaseModel):
    user_id: str
    message: str
    history: list[dict] = []


class AskResponse(BaseModel):
    reply: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    return AskResponse(reply=f"Placeholder reply. You said: {req.message}")


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(413, "File too large (20 MB max)")
    if not data.startswith(b"%PDF-"):
        raise HTTPException(400, "Only PDF files are supported")
    try:
        pages = extract_pages(data)
    except Exception:
        raise HTTPException(400, "Could not read this PDF")
    if not pages:
        raise HTTPException(422, "No text found. Scanned PDFs are not supported yet")
    chunks = chunk_pages(pages)
    return {
        "pages_with_text": len(pages),
        "chunks": len(chunks),
        "preview": [asdict(c) for c in chunks[:3]],
    }
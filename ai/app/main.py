# app/main.py
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pypdf import PdfReader
from dotenv import load_dotenv
from app.store import add_pdf, read_pdf, search_chunks, get_user_documents, get_all_users
import logging
from app.reg_service import generate_rag_answer
from app.db import init_db
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
load_dotenv()



@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Academic RAG API", lifespan=lifespan)


@app.post("/api/ask")
async def ask_endpoint(
    user_id: str = Form(...),
    query: str = Form(...),
        document_id: str | None = Form(None),          # restored: ask about an existing document

    top_k: int = Form(5),
file: UploadFile = File(None), 
):
    if isinstance(file, str) or (file is not None and not file.filename):
        file = None
    try:
        if file is not None:
            document_id = document_id or Path(file.filename or "").stem or str(uuid.uuid4())
            data= await read_pdf(file)
            await run_in_threadpool(add_pdf,user_id,document_id,data)
        

        # Pass extracted PDF text or fallback to database search
        result =await run_in_threadpool(generate_rag_answer,
            user_id=user_id,
            query=query,
            document_id=document_id,
            top_k=top_k
        )
        return {**result, "document_id": document_id}   # the client reuses this id later
    except HTTPException:
        raise  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Add this to your app/main.py
@app.get("/api/documents/{user_id}")
def list_user_documents(user_id: str):
    try:
        documents = get_user_documents(user_id=user_id)
        return {"user_id": user_id, "documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/users")
def list_users():
    try:
        users = get_all_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
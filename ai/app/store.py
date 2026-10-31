# app/store.py
from app.chunking import Chunk, chunk_pages
from app.db import SessionLocal, ChunkModel
from sqlalchemy import select, distinct
from app.embeddings import embed_texts
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB

def get_all_users():
    db = SessionLocal()
    try:
        stmt = select(distinct(ChunkModel.user_id))
        results = db.execute(stmt).scalars().all()
        return [{"user_id": uid} for uid in results if uid]
    finally:
        db.close()

def get_user_documents(user_id: str):
    db = SessionLocal()
    try:
        stmt = select(distinct(ChunkModel.document_id)).where(ChunkModel.user_id == user_id)
        results = db.execute(stmt).scalars().all()
        return [{"document_id": doc_id} for doc_id in results if doc_id]
    finally:
        db.close()

def replace_document(user_id: str, document_id: str, chunks: list[Chunk], vectors) -> None:
    with SessionLocal() as session:
        session.query(ChunkModel).filter_by(
            user_id=user_id, document_id=document_id
        ).delete()
        
        new_chunks = [
            ChunkModel(
                user_id=user_id,
                document_id=document_id,
                page=c.page,
                chunk_index=c.index,
                content=c.text,
                embedding=v
            )
            for c, v in zip(chunks, vectors)
        ]
        session.add_all(new_chunks)
        session.commit()
def add_pdf(user_id:str , document_id:str , data:bytes):
    chunks=chunk_pages(pdf_bytes=data)
    embedding_chunks=embed_texts(texts=[c.text for c in chunks])
    replace_document(user_id,document_id,chunks,vectors=embedding_chunks)
    return {
        "document_id":document_id
    }
async def read_pdf(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(413, "File too large (20 MB max)")
    if not data.startswith(b"%PDF-"):
        raise HTTPException(400, "Only PDF files are supported")
    return data

def search_chunks(user_id: str, query_vector, top_k: int = 5, document_id: str | None = None):
    with SessionLocal() as session:
        distance_expr = ChunkModel.embedding.cosine_distance(query_vector)
        score_expr = (1 - distance_expr).label("score")
        
        query = session.query(
            ChunkModel.document_id,
            ChunkModel.page,
            ChunkModel.chunk_index,
            ChunkModel.content,
            score_expr
        ).filter(ChunkModel.user_id == user_id)
        
        if document_id:
            query = query.filter(ChunkModel.document_id == document_id)
            
        query = query.order_by(distance_expr).limit(top_k)
        rows = query.all()
        
        return [
            {
                "document_id": r.document_id,
                "page": r.page,
                "chunk_index": r.chunk_index,
                "content": r.content,
                "score": round(float(r.score), 4),
            }
            for r in rows
        ]
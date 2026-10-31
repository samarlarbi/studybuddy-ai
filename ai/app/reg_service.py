# from openai import OpenAI
# from app.store import search_chunks
# from app.embeddings import embed_texts
# client=OpenAI()
# def generate_rag_answer(user_id:str,query:str,document_id:str|None=None,top_k:int=5):
#     try:
#         query_emb=embed_texts([query])
#         query_emb=query_emb[0].tolist()

#         soucechunks=search_chunks(user_id=user_id ,query_vector=query,top_k=top_k,document_id=document_id)
#         if SourceChunk==[]:
#             return 'nothing'
#         context_para = "\n".join([  "document_id"+ c.document_id+
#                 "page"+c.page+ 
#                 "chunk_index"+ c.chunk_index+
#                 "content"+ c.content+
#                 "score"+ c.score
#                 for c in SourceChunk
#               ]   )
#         sys_prompt="looking at thes chunkes retrieve the perfect answer for the user question using only the provided context dont make up any answer outside the context i gave u if the contest is not realy have the answer just say that u dont have the correct info for the qustion given"
#         user_pompt="the context : " + context_para + " \n the user question : "+ query
#         responce = client.chat.completions.create(
#             model="",
#             messages=[{
#                 "role":"system","content":sys_prompt,
#                 "role":"user","content":user_pompt
#             }],
#             temperature=0.1
#         ),
#         answer = response.choices[0].message.content
#         return {
#             "answer": answer,
#             "sources": retrieved_chunks
#         }

#     except Exception as e:
#         raise RuntimeError(f"RAG pipeline error: {str(e)}")
        
# app/reg_service.py
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from app.store import search_chunks
from app.embeddings import embed_texts

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def generate_rag_answer(
    user_id: str, 
    query: str, 
    document_id: str | None = None, 
    top_k: int = 5
):
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing from your environment variables or .env file.")
        
        client = OpenAI(api_key=api_key)

        # SCENARIO A: User provided custom document text directly in the request
       
        # SCENARIO B: Normal flow — search the database using pgvector
        query_emb = embed_texts([query])
        query_vector = query_emb[0].tolist()

        retrieved_chunks = search_chunks(
            user_id=user_id, 
            query_vector=query_vector, 
            top_k=top_k, 
            document_id=document_id
        )

        if not retrieved_chunks:
            return {
                "answer": "I don't have the correct info for the question given.",
                "sources": []
            }

        context_para = "\n\n".join([
            f"document_id: {c['document_id']} | page: {c['page']} | chunk_index: {c['chunk_index']} | content: {c['content']} | score: {c['score']}"
            for c in retrieved_chunks
        ])

        sys_prompt = (
            "Looking at these chunks, retrieve the perfect answer for the user question "
            "using only the provided context. Don't make up any answer outside the context. "
            "If the context does not really have the answer, just say that you don't have "
            "the correct info for the question given."
            "Note : the query sometimes comes with paragraph or text along side if the text looks like its usfull for the question answer  u can add that to the context  "
        )
        
        user_prompt = f"The context:\n{context_para}\n\nThe user question: {query}"

        response = client.chat.completions.create(
            model="gpt-6-luna",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )


        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "sources": retrieved_chunks
        }

    except Exception as e:
        raise RuntimeError(f"RAG pipeline error: {str(e)}")
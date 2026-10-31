from pydantic import BaseModel
from typing import List,Optional


class QueryReq(BaseModel):
    user_id:str
    query:str
    top_q:Optional[int]=5
    document_id:Optional[str]=None

class SourceChunk(BaseModel):
    document_id:str
    page:int
    chunk_index:int
    content:str
    score:float
class QueryRes(BaseModel):
    answer:str
    souces:List[SourceChunk]
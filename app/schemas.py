from pydantic import BaseModel, Field
from typing import List, Optional

class QueryInput(BaseModel):
    query: str = Field(..., example="Bagaimana cara mengajukan cuti?")
    top_k: Optional[int] = Field(3)
    threshold: Optional[float] = Field(0.9)

class DocumentSource(BaseModel):
    doc_title: str
    section_title: str
    doc_version: str

class RAGResponse(BaseModel):
    answer: str
    confidence_label: str
    reason_code: str
    sources: List[DocumentSource] = Field(default=[])
import traceback
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.ingest_doc import run_markdown_ingestion
from app.schemas import QueryInput, RAGResponse
from app.service.agent import AgenticRouter
from pathlib import Path
logger = logging.getLogger("uvicorn.error")
router = APIRouter()

@router.post("/api/v1/chat", response_model=RAGResponse)
async def chat_endpoint(payload: QueryInput):
    try:
        response = await AgenticRouter.process_request(payload)
        return response
    except Exception as e:
        logger.error(f"Error pada chat_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error: {str(e)}"
        )

@router.get("/")
async def root():
    return {
        "message": "Aplikasi RAG NusantaraCare",
        "status": "ok"
        }
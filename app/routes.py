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

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Memeriksa data SOP baru untuk di-ingest...")
    base_path = Path(__file__).resolve().parent  
    f_path = base_path / "app" / "nusantaracare_panduan_operasional_internal_v2.md"
    
    run_markdown_ingestion(
        file_path=f_path, 
        doc_title="Panduan Operasional Internal NusantaraCare", 
        version="2.0"
    )
    yield
    print("[Shutdown] Mematikan layanan RAG.")

app = FastAPI(
    title="NusantaraCare RAG System",
    version="0.1.0",
    lifespan=lifespan
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        print(f" ERROR TERJADI PADA: {request.url.path}")
        
        traceback.print_exception(*sys.exc_info())
        print("="*50 + "\n")
        
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal Server Error: {str(exc)}"}
        )

@app.post("/api/v1/chat", response_model=RAGResponse)
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

@app.get("/")
async def root():
    return {
        "message": "Aplikasi RAG NusantaraCare",
        "status": "ok"
        }
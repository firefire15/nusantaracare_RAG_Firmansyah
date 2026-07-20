from fastapi import FastAPI

from app.routes import router
from contextlib import asynccontextmanager
from app.ingest_doc import run_markdown_ingestion
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("[Startup] Memeriksa data SOP baru untuk di-ingest...")
        base_path = Path(__file__).resolve().parent  
        f_path = base_path / "app" / "document"/"nusantaracare_panduan_operasional_internal_v2.md"
        run_markdown_ingestion(
            file_path=f_path, 
            doc_title="Panduan Operasional Internal NusantaraCare", 
            version="2.0"
        )
        yield
        print("[Shutdown] Mematikan layanan RAG.")
    except:
        raise

app = FastAPI(
    title="NusantaraCare RAG System",
    version="0.1.0",
    lifespan=lifespan
)
app.include_router(router)


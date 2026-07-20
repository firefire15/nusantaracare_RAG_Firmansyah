import os
from datetime import datetime
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from app.service.rag import rag_pipeline
from app.service.config import get_openai_client     
from datetime import datetime
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def run_markdown_ingestion(file_path: str, doc_title: str, version: str):
    try:
        if not os.path.exists(file_path):
            print(f"[Ingestion] File {file_path} tidak ditemukan. Melewati proses otomatisasi.")
            return

        collection = rag_pipeline.collection

        existing_count = collection.count()
        if existing_count > 0:
            print(f"[Ingestion] Database sudah terisi ({existing_count} chunks). Melewati proses chunking & embedding.")
            return

        print(f"[Ingestion] Membaca file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(markdown_text)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        splits = text_splitter.split_documents(md_header_splits)

        print(f"[Ingestion] Mempersiapkan data untuk {len(splits)} chunk dokumen...")
        
        texts_to_embed = []
        chunk_ids = []
        metadatas = []

        for index, chunk in enumerate(splits):
            doc_id = f"DOC_{doc_title.upper().replace(' ', '_')}_{version}"
            chunk_id = f"{doc_id}_CHUNK_{index}"
            section_title = chunk.metadata.get("Header 2", chunk.metadata.get("Header 1", "Umum"))
            section_subtitle = chunk.metadata.get("Header 3", chunk.metadata.get("Header 2", chunk.metadata.get("Header 1", "Umum")))

            is_active = True
            effective_date = "2026-07-01"
            effective_until = ""

            if section_subtitle and ("NONAKTIF" in section_subtitle or "nonaktif" in section_subtitle):
                is_active = False
                effective_date = "2025-01-01"
                effective_until = "2026-06-30"

            metadata = {
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "doc_title": doc_title,
                "section_title": section_title,
                "section_subtitle": section_subtitle,
                "effective_date": effective_date,
                "effective_until": effective_until,
                "doc_version": version,
                "is_active": is_active, 
                "created_at": datetime.now().isoformat()
            }

            texts_to_embed.append(chunk.page_content)
            chunk_ids.append(chunk_id)
            metadatas.append(metadata)

        print(f"[Ingestion] Mengambil embedding dari Notispace untuk {len(texts_to_embed)} chunk...")

        client = get_openai_client()
        response = client.embeddings.create(
            model=os.getenv("EMBEDDING_MODEL_NAME", "notispace/ns-embed"),
            input=texts_to_embed,
        )
        calculated_embeddings = [d.embedding for d in response.data]

        print("[Ingestion] Memasukkan data vektor ke ChromaDB...")
        collection.upsert(
            documents=texts_to_embed,
            metadatas=metadatas,
            embeddings=calculated_embeddings, 
            ids=chunk_ids
        )
        print("[Ingestion] Database berhasil diperbarui via Notispace SDK dan siap digunakan.")
    except:
        raise
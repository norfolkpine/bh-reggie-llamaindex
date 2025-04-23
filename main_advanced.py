from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from llama_index.readers.gcs import GCSReader
from llama_index.readers.google import GoogleDriveReader
from llama_index.core import VectorStoreIndex, StorageContext
from sqlalchemy import create_engine
from llama_index.vector_stores.postgres import PGVectorStore
from django.conf import settings
import os
import django

django.setup()

from apps.reggie.models import KnowledgeBase

app = FastAPI()

# ENV VARS
GCS_BUCKET = os.getenv("GCS_BUCKET")
POSTGRES_URL = os.getenv("POSTGRES_URL")

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

class IngestRequest(BaseModel):
    gcs_path: str
    knowledgebase_id: str

class DriveIngestRequest(BaseModel):
    folder_id: str
    knowledgebase_id: str

def get_kb_and_vector_store(kb_id):
    try:
        kb = KnowledgeBase.objects.get(knowledgebase_id=kb_id)
    except KnowledgeBase.DoesNotExist:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")

    embedder = kb.get_embedder()
    engine = create_engine(POSTGRES_URL)
    vector_store = PGVectorStore(
        engine=create_engine(POSTGRES_URL),
        table_name=kb.vector_table_name,
        embed_dim=embedder.dimensions
    )

    return kb, embedder, vector_store

@app.post("/ingest")
async def ingest_file(payload: IngestRequest):
    if not any(payload.gcs_path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
        return {"status": "skipped", "reason": "unsupported file type"}

    reader = GCSReader(bucket=GCS_BUCKET, prefix=payload.gcs_path)
    documents = reader.load_data()

    kb, embed_model, vector_store = get_kb_and_vector_store(payload.knowledgebase_id)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)

    return {"status": "success", "file": payload.gcs_path, "documents": len(documents)}

@app.post("/ingest-all")
async def ingest_all(payload: IngestRequest):
    reader = GCSReader(bucket=GCS_BUCKET, prefix=payload.gcs_path)
    documents = reader.load_data()
    documents = [
        doc for doc in documents
        if any(doc.metadata.get("file_path", "").endswith(ext) for ext in SUPPORTED_EXTENSIONS)
    ]

    kb, embed_model, vector_store = get_kb_and_vector_store(payload.knowledgebase_id)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)

    return {"status": "success", "files": len(documents)}

@app.post("/ingest-drive")
async def ingest_drive(payload: DriveIngestRequest):
    reader = GoogleDriveReader()
    documents = reader.load_data(folder_id=payload.folder_id)

    kb, embed_model, vector_store = get_kb_and_vector_store(payload.knowledgebase_id)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)

    return {"status": "success", "folder_id": payload.folder_id, "documents": len(documents)}

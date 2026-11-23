from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, status

from app.models import Document, DocumentCreate, DocumentUpdate

app = FastAPI(title="rag-agent-fastapi", version="0.1.0")

# Vorläufiger In-Memory-Speicher – wird an Tag 3 durch PostgreSQL ersetzt
_documents: dict[UUID, Document] = {}


def _get_or_404(doc_id: UUID) -> Document:
    doc = _documents.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def create_document(payload: DocumentCreate) -> Document:
    doc = Document(
        id=uuid4(),
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    _documents[doc.id] = doc
    return doc


@app.get("/documents")
async def list_documents(
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Document]:
    return list(_documents.values())[offset : offset + limit]


@app.get("/documents/{doc_id}")
async def get_document(doc_id: UUID) -> Document:
    return _get_or_404(doc_id)


@app.patch("/documents/{doc_id}")
async def update_document(doc_id: UUID, payload: DocumentUpdate) -> Document:
    doc = _get_or_404(doc_id)
    updated = doc.model_copy(update=payload.model_dump(exclude_unset=True))
    _documents[doc_id] = updated
    return updated


@app.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: UUID) -> None:
    _get_or_404(doc_id)
    del _documents[doc_id]
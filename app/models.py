from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    source_url: str | None = None


class DocumentCreate(DocumentBase):
    """Eingabe für POST /documents."""


class DocumentUpdate(BaseModel):
    """Eingabe für PATCH – alle Felder optional."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    source_url: str | None = None


class Document(DocumentBase):
    """Ausgabe – inkl. serverseitig erzeugter Felder."""
    id: UUID
    created_at: datetime

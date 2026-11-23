from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import _documents, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_store():
    _documents.clear()


def _create(title: str = "Doc", content: str = "Text") -> dict:
    resp = client.post("/documents", json={"title": title, "content": content})
    assert resp.status_code == 201
    return resp.json()


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get():
    doc = _create("First Steps")
    resp = client.get(f"/documents/{doc['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "First Steps"


def test_list_with_limit():
    for i in range(3):
        _create(f"Doc {i}")
    assert len(client.get("/documents?limit=2").json()) == 2


def test_create_rejects_empty_title():
    resp = client.post("/documents", json={"title": "", "content": "x"})
    assert resp.status_code == 422


def test_get_unknown_returns_404():
    assert client.get(f"/documents/{uuid4()}").status_code == 404


def test_patch_only_changes_sent_fields():
    doc = _create("Old", "Content stays")
    resp = client.patch(f"/documents/{doc['id']}", json={"title": "New"})
    assert resp.json()["title"] == "New"
    assert resp.json()["content"] == "Content stays"


def test_delete():
    doc = _create()
    assert client.delete(f"/documents/{doc['id']}").status_code == 204
    assert client.get(f"/documents/{doc['id']}").status_code == 404
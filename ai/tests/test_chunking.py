import pytest
from fastapi.testclient import TestClient

from app.chunking import chunk_pages, chunk_text
from app.main import app

client = TestClient(app)


def test_short_text_is_one_chunk():
    assert chunk_text("hello world") == ["hello world"]


def test_chunks_respect_size_limit():
    for piece in chunk_text("word " * 1000, size=300, overlap=50):
        assert len(piece) <= 300


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("x", size=100, overlap=100)


def test_chunks_keep_their_page_numbers():
    pages = [(1, "a " * 600), (2, "b " * 600)]
    chunks = chunk_pages(pages, size=300, overlap=50)
    assert {c.page for c in chunks} == {1, 2}
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_ingest_rejects_non_pdf():
    r = client.post("/ingest", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_chunks_start_and_end_on_word_boundaries():
    words = [f"word{i}" for i in range(400)]
    valid = set(words)
    for piece in chunk_text(" ".join(words), size=300, overlap=60):
        tokens = piece.split()
        assert tokens[0] in valid
        assert tokens[-1] in valid
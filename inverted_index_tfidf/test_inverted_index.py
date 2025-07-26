from .inverted_index import InvertedIndex

def test_add_single_document_and_search():
    index = InvertedIndex()
    index.add_document("doc1", "hello world")
    results = index.search("hello")

    assert len(results) == 1
    assert results[0].doc_id == "doc1"
    assert results[0].score > 0

def test_search_nonexistent_term_returns_empty():
    index = InvertedIndex()
    index.add_document("doc1", "hello world")
    results = index.search("foo")
    assert len(results) == 0


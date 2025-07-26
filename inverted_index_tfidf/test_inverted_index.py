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


def test_multi_docs_simple_ranking():
    index = InvertedIndex()
    index.add_document("doc1", "hello world")
    index.add_document("doc2", "hello hello world and")
    results = index.search("hello")
    assert len(results) == 2

    doc_scores = {r.doc_id: r.score for r in results}
    assert doc_scores["doc2"] > doc_scores["doc1"]

def test_idf_ranking_rare_terms_score_higher():
    index = InvertedIndex()
    index.add_document("doc1", "common word rose")
    index.add_document("doc2", "common word orchid")
    index.add_document("doc3", "common word nasturtium")
    index.add_document("doc4", "common word common")

    rare_results = index.search("rose")
    common_results = index.search("common")

    rose_score = rare_results[0].score
    common_score = common_results[0].score

    assert rose_score > common_score

def test_multi_term_query_ranking():
    index = InvertedIndex()
    index.add_document("doc1", "soup recipe")
    index.add_document("doc2", "mashed potatoes recipe")
    index.add_document("doc3", "ice cream recipe")
    index.add_document("doc4", "ice cream cake recipe")
    index.add_document("doc5", "asparagus recipe")

    results = index.search("ice cream cake recipe")

    assert len(results) == 5
    assert results[0].doc_id == "doc4"

    scores = {r.doc_id: r.score for r in results}
    assert scores["doc4"] > scores["doc3"]
    assert scores["doc3"] > scores["doc1"]


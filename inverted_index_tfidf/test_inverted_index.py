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


def test_max_results_limit():
    index = InvertedIndex()
    for i in range(100):
        index.add_document(f"doc{i}", f"recipe {i}")

    all_results = index.search("recipe")  # default is 10
    assert len(all_results) == 10

    limited_results = index.search("recipe", max_results=3)
    assert len(limited_results) == 3

    for i in range(2):
        assert limited_results[i].score >= limited_results[i + 1].score


def test_empty_query_returns_empty_results():
    index = InvertedIndex()
    index.add_document("doc1", "hello world")
    assert index.search("") == []
    assert index.search("   ") == []


def test_non_matching_query_returns_empty_results():
    index = InvertedIndex()
    index.add_document("doc1", "hello world")
    assert index.search("wow") == []
    assert index.search("ok") == []


def test_update_document():
    index = InvertedIndex()
    index.add_document("doc1", "hello world")

    results = index.search("hello")
    assert len(results) == 1
    assert index.search("foo") == []

    index.add_document("doc1", "foo")
    foo_results = index.search("foo")
    assert len(foo_results) == 1
    assert foo_results[0].doc_id == "doc1"


def test_remove_document():

    index = InvertedIndex()
    index.add_document("doc1", "hello world")
    index.add_document("doc2", "foo bar")

    results = index.search("hello")
    assert len(results) == 1

    index.remove_document("doc1")
    new_results = index.search("hello")
    assert len(new_results) == 0

    alt_results = index.search("foo")
    assert len(alt_results) == 1


def test_get_stats():
    index = InvertedIndex()
    index.add_document("1", "vegetable gardening")
    index.add_document("2", "flower gardening")
    index.add_document("3", "diy gardening")

    stats = index.get_stats()
    assert stats["total_documents"] == 3
    assert stats["total_terms"] == 4
    assert stats["vocab_size"] == len(index._index)


def test_get_document_content():
    index = InvertedIndex()
    index.add_document("1", "vegetable gardening")
    index.add_document("2", "flower gardening")
    index.add_document("3", "diy gardening")

    doc1_content = index.get_document_content("1")
    assert doc1_content == "vegetable gardening"

    doc2_content = index.get_document_content("2")
    assert doc2_content == "flower gardening"

    doc3_content = index.get_document_content("3")
    assert doc3_content == "diy gardening"


def test_tokenization_edge_cases():
    index = InvertedIndex()
    index.add_document("1", "vegetable gardening!")
    index.add_document("2", "flower gardening?")
    index.add_document("3", "diy, gardening")

    gardening_results = index.search("gardening")
    assert len(gardening_results) == 3

    caps_results = index.search("gardening")
    assert len(caps_results) == 3

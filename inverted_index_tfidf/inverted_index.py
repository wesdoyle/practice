from dataclasses import dataclass
from collections import defaultdict

@dataclass
class SearchResult:
    doc_id: str
    score: float

@dataclass
class Document:
    doc_id: str
    content: str 

class InvertedIndex:
    def __init__(self):
        self._documents: dict[str, Document] = dict()
        self._index: dict[str, set[str]] = defaultdict(set)

    def add_document(self, doc_id: str, content: str) -> None:
        doc = Document(doc_id, content)
        self._documents[doc_id] = doc
        terms = self._tokenize(content)
        for term in terms:
            self._index[term].add(doc_id)

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        query_terms = self._tokenize(query)
        if not query_terms:
            return []
        matching_docs = set()
        for term in query_terms:
            matching_docs.update(self._index.get(term, set()))

        results = [SearchResult(doc_id, 1.0) for doc_id in matching_docs]
        return results[:max_results]

    def _tokenize(self, text: str) -> list[str]:
        """Naive whitespace tokenization and lowercasing"""
        return text.lower().split()

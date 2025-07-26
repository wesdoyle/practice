from dataclasses import dataclass
from collections import defaultdict, Counter
import math


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
        self._term_frequencies: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._document_lengths: dict[str, int] = dict()

    def add_document(self, doc_id: str, content: str) -> None:
        doc = Document(doc_id, content)
        self._documents[doc_id] = doc
        terms = self._tokenize(content)
        term_counts = Counter(terms)

        self._document_lengths[doc_id] = len(terms)

        for term, count in term_counts.items():
            self._index[term].add(doc_id)
            self._term_frequencies[doc_id][term] = count

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        matching_docs = set()
        for term in query_terms:
            matching_docs.update(self._index.get(term, set()))

        scored_results = []
        for doc_id in matching_docs:
            score = self._calculate_tfidf_score(doc_id, query_terms)
            scored_results.append(SearchResult(doc_id, score))

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:max_results]

    def _calculate_tfidf_score(self, doc_id: str, query_terms: list[str]) -> float:
        score = 0.0
        total_docs = len(self._documents)

        for term in query_terms:
            # TF
            tf = self._term_frequencies[doc_id].get(term, 0)
            if tf == 0:
                continue

            # IDF
            docs_with_term = len(self._index[term])
            idf = math.log((1 + total_docs) / docs_with_term) if docs_with_term > 0 else 0
            score += tf * idf

        return score

    def _tokenize(self, text: str) -> list[str]:
        """Naive whitespace tokenization and lowercasing"""
        return text.lower().split()

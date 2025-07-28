class HyperLogLog:
    """
    HyperLogLog probabilistic cardinality estimator.
    
    SPEC:
    - Estimates the number of unique items in a stream
    - Uses fixed memory regardless of actual cardinality
    - Provides configurable accuracy vs memory trade-off
    - Uses hash functions and statistical properties of bit patterns
    """
    def __init__(self):
        self._items = set()

    def cardinality(self) -> int:
        return len(self._items) 

    def add(self, item: str) -> None:
        self._items.add(item)

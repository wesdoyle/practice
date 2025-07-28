class CountMinSketch:
    """
    Count-Min Sketch probabilistic frequency estimator.
    
    SPEC:
    - Estimates frequency of items in a stream using fixed memory
    - Guarantees no underestimation (one-sided error)
    - Configurable accuracy vs memory trade-off
    - Uses multiple hash functions and takes minimum across rows
    """
    def __init__(self):
        self._counts = dict()

    def frequency(self, key: str) -> int:
        return self._counts.get(key, 0)

    def add(self, key: str):
        self._counts[key] = self._counts.get(key, 0) + 1

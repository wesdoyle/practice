import hashlib
import array


class CountMinSketch:
    """
    Count-Min Sketch probabilistic frequency estimator.

    SPEC:
    - Estimates frequency of items in a stream using fixed memory
    - Guarantees no underestimation (one-sided error)
    - Configurable accuracy vs memory trade-off
    - Uses multiple hash functions and takes minimum across rows
    """

    def __init__(self, width: int = 100, depth: int = 4):
        if not (isinstance(width, int) and width > 0):
            raise ValueError("width must be a positive integer")
        if not (isinstance(depth, int) and depth > 0):
            raise ValueError("depth must be a positive integer")

        self._width = width
        self._depth = depth
        self._matrix = [array.array('L', [0] * width) for _ in range(depth)]

    def _hash(self, encoded_key: bytes, seed: int) -> int:
        hash_input = encoded_key + str(seed).encode("utf-8")
        return int(hashlib.sha256(hash_input).hexdigest(), 16) % self._width


    def frequency(self, key: str) -> int:
        encoded_key = key.encode("utf-8")
        estimates = []
        for row in range(self._depth):
            col = self._hash(encoded_key, row)
            estimates.append(self._matrix[row][col])
        return min(estimates)


    def add(self, key: str, count:int=1):
        encoded_key = key.encode("utf-8")
        for row in range(self._depth):
            col = self._hash(encoded_key, row)
            self._matrix[row][col] += count

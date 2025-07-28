import hashlib


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
        self._counts = dict()
        self._width = width
        self._depth = depth
        self._matrix = [bytearray(width) for _ in range(depth)]

    def _hash(self, key: str | bytes, seed: str | int):
        if isinstance(key, str):
            encoded_key = key.encode("utf-8")
        else:
            encoded_key = key

        hash_input = encoded_key + str(seed).encode("utf-8")

        return int(hashlib.sha256(hash_input).hexdigest(), 16) % self._width


    def frequency(self, key: str) -> int:
        estimates = []
        for row in range(self._depth):
            col = self._hash(key, row)
            estimates.append(self._matrix[row][col])
        return min(estimates)


    def add(self, key: str, count:int=1):
        for row in range(self._depth):
            col = self._hash(key, row)
            new_val = min(self._matrix[row][col] + count, 255)
            self._matrix[row][col] = new_val

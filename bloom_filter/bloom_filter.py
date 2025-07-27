import hashlib
import math


class BloomFilter:

    def __init__(self, expected_items: int = 1_000, false_pos_rate: float = 0.01):
        self._expected_items = expected_items
        self._false_pos_rate = false_pos_rate

        self._bit_array_size = self._calculate_optimal_size(expected_items, false_pos_rate)
        self._num_hash_fns = self._calculate_optimal_hash_count(self._bit_array_size, expected_items)

        self._num_words = (self._bit_array_size + 63) // 64  # round up
        self._bit_words = [0] * self._num_words 

    def _set_bit(self, bit_index: int) -> None:
        word_index = bit_index // 64
        bit_offset = bit_index % 64
        self._bit_words[word_index] |= (1 << bit_offset)

    def _get_bit(self, bit_index: int) -> bool:
        word_index = bit_index // 64
        bit_offset = bit_index % 64
        return bool(self._bit_words[word_index] & (1 << bit_offset))

    def contains(self, key: str):
        hash_vals = self._hash(key)
        for h in hash_vals:
            if not self._get_bit(h):
                return False
        return True

    def add(self, key: str):
        hash_vals = self._hash(key)
        for h in hash_vals:
            self._set_bit(h)

    def _calculate_optimal_size(self, expected_items: int, false_pos_rate: float) -> int:
        """
        Calculate the optimal bit array size (m) for a Bloom filter.
        Ensures a balance between space efficiency and accuracy.

        Given:
        - n: expected number of elements to store
        - p: desired false positive probability

        This formula minimizes memory usage while achieving the target false positive rate:
            m = -(n * ln(p)) / (ln(2)^2)

        It is derived by:
        - Estimating the probability a bit remains 0 after n insertions with k hash functions
        - Solving for m under the assumption of optimal k (i.e., k = (m/n) * ln(2))
        """

        return int(-expected_items * math.log(false_pos_rate) / math.log(2) ** 2)

    def _calculate_optimal_hash_count(self, optimal_bit_array_size: int, expected_items: int) -> int:
        return max(1, int((optimal_bit_array_size/expected_items) * math.log(2)))

    def _hash(self, item: str) -> list[int]:
        """
        Generate k hash values for a given item using double hashing.

        This method avoids the need for multiple independent hash functions by combining
        two cryptographic hashes (md5 and sha256) to simulate k distinct hashes:
            h_i(x) = (hash1 + i * hash2) % m

        This approach is efficient, deterministic, and works well in simple Bloom filter contexts.
        String inputs are encoded to UTF-8 to ensure compatibility with byte-based hash functions, 
        as are used here.
        """
        encoded_item = item 
        if isinstance(item, str):
            encoded_item = item.encode("utf-8")

        # two hash fns
        hash_1 = int(hashlib.md5(encoded_item).hexdigest(), 16)
        hash_2 = int(hashlib.sha256(encoded_item).hexdigest(), 16)

        hashes = []
        for i in range(self._num_hash_fns):
            h = (hash_1 + i * hash_2) % self._bit_array_size
            hashes.append(h)
        return hashes


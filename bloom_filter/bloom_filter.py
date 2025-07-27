import hashlib
import math


class BloomFilter:
    """
    Rudimentary implementation of a Bloom filter.

    False positive matches are possible, but false negatives are not. This implementation
    uses a bit array and a set of hash functions to determine membership. The size of
    the bit array and the number of hash functions are determined by the expected
    number of items and the desired false positive rate.
    """

    def __init__(self, expected_items: int = 1_000, false_pos_rate: float = 0.01):
        """
        Initializes a BloomFilter object.

        Args:
            expected_items (int): The expected number of items to be stored in the filter.
            false_pos_rate (float): The desired false positive rate.
        """
        self._expected_items = expected_items
        self._false_pos_rate = false_pos_rate

        self._bit_array_size = self._calculate_optimal_size(
            expected_items, false_pos_rate
        )
        self._num_hash_fns = self._calculate_optimal_hash_count(
            self._bit_array_size, expected_items
        )

        self._num_words = (self._bit_array_size + 63) // 64  # round up
        self._bit_words = [0] * self._num_words

    def _set_bit(self, bit_index: int) -> None:
        """
        Sets the bit at the given index in the bit array to 1.

        Args:
            bit_index (int): The index of the bit to set.
        """
        word_index = bit_index // 64
        bit_offset = bit_index % 64
        self._bit_words[word_index] |= 1 << bit_offset

    def _get_bit(self, bit_index: int) -> bool:
        """
        Gets the value of the bit at the given index in the bit array.

        Args:
            bit_index (int): The index of the bit to get.

        Returns:
            bool: True if the bit is set, False otherwise.
        """
        word_index = bit_index // 64
        bit_offset = bit_index % 64
        return bool(self._bit_words[word_index] & (1 << bit_offset))

    def contains(self, key: str):
        """
        Checks if an element is in the bloom filter.

        This method may return a false positive, but never a false negative.

        Args:
            key (str): The key to check for.

        Returns:
            bool: True if the element is likely in the set, False if it is definitely not.
        """
        hash_vals = self._hash(key)
        for h in hash_vals:
            if not self._get_bit(h):
                return False
        return True

    def add(self, key: str):
        """
        Adds an element to the bloom filter.

        Args:
            key (str): The key to add.
        """
        hash_vals = self._hash(key)
        for h in hash_vals:
            self._set_bit(h)

    def _calculate_optimal_size(
        self, capacity: int, false_pos_rate: float
    ) -> int:
        """
        Calculate the optimal bit array size (m) for a Bloom filter.

        This formula minimizes memory usage while achieving the target false positive rate.
        It is derived by estimating the probability a bit remains 0 after n insertions
        with k hash functions and solving for m under the assumption of an optimal k.

        (See https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/#total-size-of-a-bloom-filter)

        The formula used is:
            m = -(n * ln(p)) / (ln(2)^2)

        Args:
            expected_items (int): The expected number of elements to store (n).
            false_pos_rate (float): The desired false positive probability (p).

        Returns:
            int: The optimal bit array size (m).
        """

        return int(math.ceil(-capacity * math.log(false_pos_rate) / math.log(2) ** 2))

    def _calculate_optimal_hash_count(
        self, optimal_bit_array_size: int, expected_items: int
    ) -> int:
        """Calculate the optimal number of hash functions (k).

        The optimal number of hash functions is determined by the bit array size (m)
        and the expected number of items (n). The result is rounded up to the
        nearest integer.

        The formula used is:
            k = (m/n) * ln(2)

        Args:
            optimal_bit_array_size (int): The size of the bit array (m).
            expected_items (int): The expected number of items (n).

        Returns:
            int: The optimal number of hash functions (k), with a minimum of 1.
        """
        return max(
            1, int(math.ceil((optimal_bit_array_size / expected_items) * math.log(2)))
        )

    def _hash(self, item: str) -> list[int]:
        """Generate k hash values for a given item using double hashing.

        This method avoids the need for multiple independent hash functions by combining
        two hash functions (md5 and sha256) to simulate k distinct hashes.
        The formula for each hash is:
            h_i(x) = (hash1 + i * hash2) % m

        String inputs are encoded to UTF-8 to ensure compatibility with byte-based hash functions.

        Args:
            item (str): The item to hash.

        Returns:
            list[int]: A list of k hash values.
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

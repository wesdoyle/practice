import hashlib
import math


class HyperLogLog:
    """
    HyperLogLog probabilistic cardinality estimator.

    SPEC:
    - Estimates the number of unique items in a stream
    - Uses fixed memory regardless of actual cardinality
    - Provides configurable accuracy vs memory trade-off
    - Uses hash functions and statistical properties of bit patterns

    Useful references:
    - https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
    - https://stackoverflow.com/questions/12327004/how-does-the-hyperloglog-algorithm-work
    - https://www.geeksforgeeks.org/system-design/hyperloglog-algorithm-in-system-design/
    """

    def __init__(self, precision=4):
        self._precision = precision
        self._num_buckets = 1 << precision
        self._buckets = bytearray(self._num_buckets)

    def _hash(self, item: str | bytes) -> int:
        if isinstance(item, str):
            encoded_item = item.encode("utf-8")
        else:
            encoded_item = item
        return int(hashlib.sha256(encoded_item).hexdigest(), 16)

    def _leading_zeros(self, hash_val: int, max_bits: int = 64):
        # This is more efficient than looping.
        # For a number n, n.bit_length() is the number of bits to represent it.
        # For a number space of max_bits, leading zeros = max_bits - n.bit_length().
        # We need rho, which is leading zeros + 1 (1-based position of leftmost 1).
        # For hash_val=0, bit_length() is 0, so this returns max_bits + 1, which is what the old code did.
        return max_bits - hash_val.bit_length() + 1

    @property
    def cardinality(self) -> int:
        if all(bucket == 0 for bucket in self._buckets):
            return 0

        # basic hll formula alpha * m^2 / sum(2^(-bucket_value))
        raw_est = (
            self._alpha()
            * (self._num_buckets**2)
            / sum(2 ** (-bucket) for bucket in self._buckets)
        )

        # Small range correction from the paper
        if raw_est <= 2.5 * self._num_buckets:
            zero_buckets = self._buckets.count(0)
            if zero_buckets != 0:
                # LinearCounting
                return int(
                    self._num_buckets
                    * math.log(self._num_buckets / float(zero_buckets))
                )

        return int(raw_est)

    def _alpha(self) -> float:
        """
        Calculates the alpha constant based on number of buckets
        These are heuristics specified in the HyperLogLog paper
        "HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm"
        Flajolet, Fusy, Gandouet, and Meunier
        (https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
        """
        if self._num_buckets == 16:
            return 0.673
        elif self._num_buckets == 32:
            return 0.697
        elif self._num_buckets == 64:
            return 0.709
        return 0.7213 / (1 + 1.079 / self._num_buckets)

    def add(self, item: str | bytes) -> None:
        hash_val = self._hash(item)

        # use first "precision" bits to select bucket
        bucket_index = hash_val & ((1 << self._precision) - 1)

        # use remaining bits to count leading zeros
        remaining_bits = hash_val >> self._precision
        leading_zeros = self._leading_zeros(remaining_bits, 256 - self._precision)

        clamped_zeros = min(leading_zeros, 255)

        # update bucket with max leading zeros seen
        self._buckets[bucket_index] = max(self._buckets[bucket_index], clamped_zeros)

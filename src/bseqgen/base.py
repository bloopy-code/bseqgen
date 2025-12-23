"""core representation for binary sequences"""
from __future__ import annotations
from collections.abc import Sequence
from enum import StrEnum
import math
from typing import Iterator
__all__ = ("Direction", "BinarySequence")


class Direction(StrEnum):
    LEFT = "left"
    RIGHT = "right"


class BinarySequence:
    def __init__(self, bits: Sequence[int | str] | str) -> None:
        self.bits: tuple[int, ...] = self._validate_bits(bits)

    @staticmethod
    def _validate_bits(
        input_bits: Sequence[int | str] | str
    ) -> tuple[int, ...]:
        """Validate input bit sequences."""
        if (input_bits is None) or (not input_bits):
            raise ValueError("Input bits cannot be None or empty.")

        try:
            bits_list: tuple[int, ...] = tuple(int(bit) for bit in input_bits)
        except (TypeError, ValueError) as e:
            raise TypeError(
                "Bits must be an iterable of 0 and 1 values."
            ) from e

        if any(bit not in (0, 1) for bit in bits_list):
            raise ValueError("Bit sequence must only contain 0 or 1.")

        return bits_list

    def __str__(self) -> str:
        return self.bit_string

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"length={self.length}, "
            f"preview='{str(self)}'"
            f")"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinarySequence):
            return NotImplemented
        return self.bits == other.bits

    def __len__(self) -> int:
        return self.length

    def __iter__(self) -> Iterator[int]:
        return iter(self.bits)

    def __getitem__(self, key: int | slice) -> int | BinarySequence:
        if isinstance(key, slice):
            return BinarySequence(self.bits[key])
        return self.bits[key]

    @property
    def length(self) -> int:
        """Number of bits in sequence."""
        return len(self.bits)

    @property
    def bit_string(self) -> str:
        """Bit sequence as a string of '0's and '1's. No padding."""
        bit_str: str = "".join("1" if bit else "0" for bit in self.bits)
        return bit_str

    @property
    def as_bytes(self) -> bytes:
        """Byte representation of bit sequence (left zero padded)"""
        bit_str: str = self.bit_string
        zero_padding_len: int = (-len(bit_str)) % 8
        bit_str_padded: str = ("0" * zero_padding_len) + bit_str
        byte_conversion: bytes = int(bit_str_padded, 2).to_bytes(
            len(bit_str_padded)//8, "big"
        )

        return byte_conversion

    @property
    def hex_string(self) -> str:
        """Hex string representation of byte sequence"""
        return self.as_bytes.hex()

    @property
    def signed(self) -> tuple[int, ...]:
        """Map bits (0, 1) to (-1, +1)."""
        return tuple(1 if bit else -1 for bit in self.bits)

    @property
    def ones(self) -> int:
        """Return number of 1's in Binary Sequence"""
        return sum(self.bits)

    @property
    def zeros(self) -> int:
        """Return number of 0's in Binary Sequence"""
        return self.length - self.ones

    @property
    def balance(self) -> float:
        """Return % of 1's to 0's in Binary Sequence. (0-1)"""
        return round(self.ones / self.length, 3)

    @property
    def entropy(self) -> float:
        """
        Return Shannon entropy (bits per symbol) for balance of 1's and 0's.

        Range:
            0.0 → fully deterministic (all 0s or all 1s)
            1.0 → maximally random (balanced 0/1)
        """
        if self.length == 0:
            return 0.0

        p1 = self.ones/self.length
        p0 = 1.0 - p1

        entropy = 0.0

        for p in (p1, p0):
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 5)

    def copy_bits(self) -> BinarySequence:
        return BinarySequence(self.bits)

    def to_length(self, n: int) -> BinarySequence:
        """Repeat or truncate sequence to length n.

        Args:
            n (int): Length to convert sequence to.
        """
        if n <= 0:
            raise ValueError("Target length must be positive and not zero.")
        repeats: int = (n + self.length - 1) // self.length
        bits: tuple[int, ...] = (self.bits * repeats)[:n]
        return BinarySequence(bits)

    def shift(
            self,
            n: int,
            direction: Direction = Direction.LEFT
    ) -> "BinarySequence":
        """Shift sequence (circular)

        Args:
            n (int): How many bits to shift by.
            direction (Direction, optional): 'left' or 'right'.
                Defaults to Direction.LEFT.

        Returns:
            BinarySequence: shifted BinarySequence.
        """
        if self.length == 0:
            return self

        n = n % self.length

        if n < 0:
            n = -n
            direction = (
                Direction.RIGHT if direction == Direction.LEFT
                else Direction.LEFT
            )

        match direction:
            case Direction.LEFT:
                return BinarySequence(self.bits[n:] + self.bits[:n])
            case Direction.RIGHT:
                return BinarySequence(self.bits[-n:] + self.bits[:-n])

        raise ValueError(f"{direction} not a valid direction; 'left', 'right'")

    def autocorr(self):
        raise NotImplementedError("Auto-correlation coming soon.")

    def crosscorr(self):
        raise NotImplementedError("Cross-correlation coming soon.")

    def run_lengths(self):
        raise NotImplementedError("Consecutive runs coming soon!")

    def to_numpy(self):
        raise NotImplementedError("to_numpy coming soon.")

    def from_numpy(self):
        raise NotImplementedError("from_numpy coming soon.")

    def invert(self):
        raise NotImplementedError("invert coming soon.")

    def xor(self):
        raise NotImplementedError("xor coming soon")

    def hamming_distance(self):
        raise NotImplementedError("Hamming distance coming soon")

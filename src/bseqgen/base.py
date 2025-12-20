"""core representation for binary sequences"""
from collections.abc import Sequence
from enum import StrEnum


class Direction(StrEnum):
    LEFT = "left"
    RIGHT = "right"


class BinarySequence:
    def __init__(self, bits: Sequence[int | str] | str) -> None:
        self.bits: list[int] = self._validate_bits(bits)
        print(self.bits)

    @staticmethod
    def _validate_bits(input_bits: Sequence[int | str] | str) -> list[int]:
        """Validate input bit sequences."""
        if (input_bits is None) or (not input_bits):
            raise ValueError("Input bits cannot be None or empty.")

        try:
            bits_list: list[int] = [int(bit) for bit in input_bits]
        except (TypeError, ValueError) as e:
            raise TypeError(
                "Bits must be an iterable of 0 and 1 values."
            ) from e

        if any(bit not in (0, 1) for bit in bits_list):
            raise ValueError("Bit sequence must only contain 0 or 1.")

        return bits_list

    def __str__(self) -> str:
        if self.length <= 64:
            return self.bit_string
        return f"{self.bit_string[:32]}...{self.bit_string[-32:]}"

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
    def signed(self) -> list[int]:
        """Map bits (0, 1) to (-1, +1)."""
        return [1 if bit else -1 for bit in self.bits]

    def to_length(self, n: int) -> "BinarySequence":
        """Repeat or truncate sequence to length n.

        Args:
            n (int): Length to convert sequence to.
        """
        if n <= 0:
            raise ValueError("Target length must be positive and not zero.")
        repeats: int = (n + self.length - 1) // self.length
        bits: list[int] = (self.bits * repeats)[:n]
        return BinarySequence(bits)

    def shift(self, n: int, direction: Direction = Direction.LEFT):
        if Direction.LEFT:
            return self.bits[n:] + self.bits[:n]
        elif Direction.RIGHT:
            return self.bits[-n:] + self.bits[:-n]
        else:
            raise ValueError("Incorrect Direction.")

    def autocorr(self):
        return None

    def crosscorr(self):
        return None

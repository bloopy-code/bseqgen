"""m-sequence"""

from __future__ import annotations

from math import gcd

from .base import BinarySequence
from .utils import (
    _check_initial_fill,
    _validate_polynomial,
    berlekamp_massey,
    calculate_canonical_frobenius,
    coeffs_to_poly_str,
    recover_fill,
)

__all__ = ("MSequence",)


class MSequence(BinarySequence):
    def __init__(self, polynomial: str, initial_fill: str) -> None:
        self.polynomial: str = polynomial.replace(" ", "")
        self.degrees: list[int] = _validate_polynomial(self.polynomial)
        self.m: int = self.degrees[0]
        self.tap_degrees: list[int] = self.degrees[1:-1]
        self.initial_fill: tuple[int, ...] = tuple(
            int(b) for b in _check_initial_fill(self.m, initial_fill)
        )

        bits = self._generate_sequence()
        super().__init__(bits)

        self.reset()

    @property
    def max_sequence_length(self) -> int:
        m_len: int = (1 << self.m) - 1
        return m_len

    def reset(self) -> None:
        self._register: tuple[int, ...] = self.initial_fill
        self._out_bit: list[int] = []

    @property
    def current_register(self) -> tuple[int, ...]:
        return self._register

    @property
    def running_output(self) -> tuple[int, ...]:
        return tuple(self._out_bit)

    def __repr__(self) -> str:
        preview = self.bit_string[: min(self.length, 32)]
        if self.length > 32:
            preview += "..."
        return (
            f"{type(self).__name__}("
            f"m={self.m}, "
            f"poly='{self.polynomial}', "
            f"original fill='{self.initial_fill}', "
            f"length={self.length}, "
            f"seq preview='{preview}'"
            f")"
        )

    def step(self) -> int:
        """Advance LFSR by one step and return the next output bit
        from the register.

        Notes:
            - Output bit is leftmost register bit: `register[0]`.
            - Register bits shift left by one position.
            - Feedback bit is inserted at the rightmost position.
            - Polynomial is in descending degree form.
            - Tap degrees refer to polynomial terms `x^k`.
            - A tap at degree `k` selects register bit index `(m-k-1)`.


        Examples:
            >>> a = MSequence("x^3+x+1", "010")
            >>> a.step()
            0
            >>> a.step()
            1

        Returns:
            int: Output bit (0 or 1).
        """
        register = self._register
        out_bit: int = register[0]

        fb = out_bit
        for k in self.tap_degrees:
            idx = self.m - k - 1
            fb ^= register[idx]

        self._register = register[1:] + (fb,)
        self._out_bit.append(out_bit)
        return out_bit

    def _generate_sequence(self) -> tuple[int, ...]:
        """Generate one full m-sequence period."""
        self.reset()
        out = tuple(self.step() for _ in range(self.max_sequence_length))
        return out

    def generate_k_bits(self, k: int, reset_on_finish: bool = True) -> BinarySequence:
        """Generate k bits of sequence from the LFSR. This can be larger,
        or smaller than the max length sequence.

        In cases where k < 2^m - 1, the sequence will only be stepped k times, and
        in cases where k > 2^m - 1, the sequence will start repeating.

        Args:
            k (int): How many bits to generate.
            reset_on_finish (bool, optional): Reset output sequence and
                LFSR register after running this method. Defaults to True.

        Returns:
            BinarySequence: Binary Seqence object.
        """
        if k <= 0:
            raise ValueError("length (k) must be positive.")
        out = tuple(self.step() for _ in range(k))

        if reset_on_finish:
            self.reset()

        return BinarySequence(out)

    def decimate(self, d: int) -> MSequence:
        """Decimate an m-sequence by factor d.
        Returns a decimated version of this m-sequence as a new MSequence.

        Decimation by factor d is defined as:
            `y[n] = x[(n*d) mod N]`

        For an m-sequence, `N = 2^m - 1`. If `gcd(d, N) = 1`, the result is another
        m-sequence (possibly with a different polynomial representation).

        Notes:
            - Decimate current sequence bits then uses Berlekamp-Massey algorithm
              to recover a polynomial for the decimated sequence, which then creates
              and returns a new MSequence from that polynomial + fill.

        Args:
            d (int): Decimation factor (must be > 0 and coprime with N). (For now!)

        Examples:
            >>> a = MSequence("x^3+x+1", "001")
            >>> a.canonical()
            MSequence(m=3,
                poly='x^3+x+1',
                original fill='(1, 0, 0)',
                length=7, seq preview='1001011'
            )

        Returns:
            MSequence: New MSequence instance representing the decimated sequence.
        """

        if d <= 0:
            raise ValueError("Decimation factor must be positive.")

        N: int = self.max_sequence_length

        if gcd(d, N) != 1:
            raise ValueError(
                f"Decimation factor {d} is not coprime with sequence length {N}."
            )  # later return this as BinarySequence instead.

        dec_bits: tuple[int, ...] = tuple(self.bits[(n * d) % N] for n in range(N))

        C = berlekamp_massey(dec_bits)
        new_poly = coeffs_to_poly_str(C)
        new_fill = recover_fill(new_poly, dec_bits)

        return MSequence(new_poly, new_fill)

    def canonical(self) -> MSequence:
        _canon_shift, _cosets, canon_seq = calculate_canonical_frobenius(self.bits)
        canon_fill = recover_fill(self.polynomial, canon_seq)

        return MSequence(self.polynomial, canon_fill)

    def lag_of(self, other: BinarySequence) -> int:
        """Return k such that self.shift(k) == other.

        Raises ValueError if other is not a cyclic shift of this sequence.
        """
        if other.length != self.length:
            raise ValueError("Length mismatch.")

        if other.bits == self.bits:
            return 0

        for k in range(1, self.length):
            if self.shift(k).bits == other.bits:
                return k

        raise ValueError("Sequence is not a cyclic shift of this m-sequence.")

"""m-sequence"""

from .base import BinarySequence
from .utils import _check_initial_fill, _validate_polynomial

__all__ = ("MSequence",)


class MSequence:
    def __init__(self, polynomial: str, initial_fill: str) -> None:
        self.polynomial = polynomial
        self.degrees = _validate_polynomial(polynomial)
        self.m = self.degrees[0]
        self.tap_degrees = self.degrees[1:-1]
        self.initial_fill = BinarySequence(_check_initial_fill(self.m, initial_fill))
        self.reset()

    @property
    def max_sequence_length(self) -> int:
        m_len: int = (1 << self.m) - 1
        return m_len

    def reset(self) -> None:
        self._register: tuple[int, ...] = self.initial_fill.bits
        self._out_bit: list[int] = []

    @property
    def current_register(self) -> BinarySequence:
        return BinarySequence(self._register)

    @property
    def running_output(self) -> tuple[int, ...]:
        return tuple(self._out_bit)

    def step(self) -> int:
        register = self._register
        out_bit: int = register[0]

        fb = out_bit
        for k in self.tap_degrees:
            idx = self.m - k - 1
            fb ^= register[idx]

        self._register = register[1:] + (fb,)
        self._out_bit.append(out_bit)
        return out_bit

    def generate_sequence(self) -> BinarySequence:
        """Generate one full m-sequence period."""
        self.reset()
        out = tuple(self.step() for _ in range(self.max_sequence_length))
        return BinarySequence(out)

    def generate_k_bits(self, n: int, reset_on_finish: bool = True) -> BinarySequence:
        if n <= 0:
            raise ValueError("length (k) must be positive.")
        out = tuple(self.step() for _ in range(n))

        if reset_on_finish:
            self.reset()

        return BinarySequence(out)

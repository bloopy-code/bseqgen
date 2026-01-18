# bseqgen

Current Version: 0.1.4

Small Python library for generating and analysing Binary Sequences, with a focus on pseudorandom binary sequences and signal-processing style operations.

> **Status:** Beta (API may evolve and change significantly before v1.0)

![PyPI](https://img.shields.io/pypi/v/bseqgen)

[![CI](https://github.com/bloopy-code/bseqgen/actions/workflows/main.yml/badge.svg)](https://github.com/bloopy-code/bseqgen/actions/workflows/main.yml)

---

## Conventions

- **Linear Feedback Shift Register**: Fibonacci LFSR where the output bit is the leftmost register bit (`register[0]`). Register shifts left, and the feedback bit is inserted at the rightmost position.

- **Polynomial Format**: Polynomials are presented in descending degree order with the constant term written as `+1`, not `x^0`.

- **Tap degrees**: Tap degrees `[k1, k2, ...]` refer to polynomial terms `x^k`. A tap at degree `k` selects register bit index `m - k - 1` where `m` is the register length (highest polynomial degree).

- **Berlekamp–Massey (BM) polynomial mapping:**  
  `utils.berlekamp_massey()` returns the connection polynomial coefficients  
  `C = [c0, c1, ..., cL]` in **ascending power order**, meaning:

  C(x) = c0 + c1·x + c2·x^2 + ... + cL·x^L

  This library converts BM output into the project’s polynomial format (`x^m+...+1`) using:

  - `m = L`
  - always include `x^m`
  - if `c_j = 1`, include term `x^(m - j)`

  ```python
  # Example BM output
  C = [1, 0, 1, 1]
  # L = 3

  # Included terms:
  # x^3 always included
  # c1 = 0 -> no x^(3-1) = x^2
  # c2 = 1 -> include x^(3-2) = x^1
  # c3 = 1 -> include x^(3-3) = x^0 = 1

  # Result:
  # x^3 + x + 1 (which is equivilent to C = [1,1,0,1])
  ```

- **Decimation**: decimation by factor `d` is defined as `y[n] = x[(n*d) mod N]` with `N` being the sequence period/length (for m-sequence: `N = 2^m - 1`).

## Features

- Tuple binary sequence representation.
- Input validation from strings, lists, tuples, etc.
- Shift sequences left/right (circular, supports negative shifts).
- Sequence repetition and truncation.
- Byte/hex/string representations.
- Basic sequence metrics (bit counts, balance, basic symbol entropy).
- bitwise `xor`, `bitwise_and`, `bitwise_or` (or use operators `^, &, |`).
- `inverted` to get inverted sequence (or use `~`).
- `to_numpy()` and `from_numpy()` for NumPy interop.
- Use `random_sequence` to generate a random binary sequence.
- `autocorr` and `crosscorr` to get correlation values between other (or same) shifted Binary Sequences.
- NOTE: Haven't yet checked or taken into consideration optimisation for very long sequences and operations - and as such currently may be slow.

---

## Installation

```bash
pip install bseqgen
```

---

## Quick Examples

```python
from bseqgen.base import BinarySequence
from bseqgen import random_sequence

# can define your own binary sequence.
seq = BinarySequence("110011")

# or use one that comes with bseqgen
random_seq = random_sequence(n=10)

# enjoy! 
print(seq.bits)
# (1, 1, 0, 0, 1, 1)

print(seq.shift(2).bits)
# (0, 0, 1, 1, 1, 1)

print(seq.ones, seq.zeros)
# 4 2

print(seq.run_lengths)
# [(1, 2), (0, 2), (1, 2)]

print(seq & BinarySequence("111000").bits)
# (1, 1, 0, 0, 0, 0)

print(seq ^ BinarySequence("111000").bits)
# (0, 0, 1, 0, 1, 1)

print(seq | BinarySequence("111000").bits)
# (1, 1, 1, 0, 1, 1)

print(~seq.bits)
# (0, 0, 1, 1, 0, 0)

seq.to_numpy()
# array([1, 1, 0, 0, 1, 1], dtype=uint8)
```

## Roadmap

Planned additions include:

- CURRENT: Max Length Sequences (m-sequence). First version release approx ~ 25th January 2026.
- PRBS generators (Gold codes, Walsh-Hadamard, Kasami and more).
- Autocorrelation and cross-correlation operations.
- Property stats and checks, and guess at what types of codes you might have and if it fits the ideal properties.
- Docstrings, documentation and formatting surge - a mid-point check to refactor, rethink and clarify code.
- Polynomial operations (multiply, divide, factorise, primitive check).

## License

MIT

## Support

Found a bug or want a feature? Please open an issue on GitHub:  
<https://github.com/bloopy-code/bseqgen/issues>

Always happy to accept contributions, collaboration, or if someone wants to check my maths!

## Resources

- M-Sequence theory inspired from this paper: McEliece, R.J. (1987). The Theory of m-Sequences. In: Finite Fields for Computer Scientists and Engineers. The Kluwer International Series in Engineering and Computer Science, vol 23. Springer, Boston, MA. <https://doi.org/10.1007/978-1-4613-1983-2_10>

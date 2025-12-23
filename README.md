# bseqgen

Small Python library for working with Binary Sequences, with a focus on pseudorandom binary sequences and signal-processing style operations.

> **Status:** Beta (API may evolve and change significantly before v1.0)

---

## Features

- Tuple binary sequence representation.
- Input validation from strings, lists, tuples, etc.
- Shift sequences left/right (circular, supports negative shifts).
- Sequence repetition and truncation.
- Byte/hex/string representations
- Basic sequence metrics (bit counts, balance, basic symbol entropy)

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
```

## Roadmap

Planned additions include:

- PRBS generators (Gold codes, Walsh-Hadamard, Kasami and more)
- Autocorrelation and cross-correlation operations.
- Run length analysis.
- NumPy interoperability.

## License

MIT.

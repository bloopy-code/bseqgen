import re
from collections.abc import Sequence
from typing import NoReturn

BitsLike = Sequence[int | str] | str | int

__all__ = [
    "BitsLike",
    "validate_bits",
    "berlekamp_massey",
    "coeffs_to_poly_str",
    "recover_fill",
    "calculate_canonical_frobenius",
]


def _validate_polynomial(polynomial: str) -> list[int]:
    # normalise whitespace
    polynomial = polynomial.replace(" ", "")

    # validate format
    polynomial_pattern = r"^(x(?:\^\d+)?)(?:\+x(?:\^\d+)?)*\+1$"
    if re.fullmatch(polynomial_pattern, polynomial) is None:
        raise ValueError(
            f"{polynomial} is in incorrect format. Expected like 'x^m+x^k+...+1'."
        )

    degree_pattern = r"x(?:\^(\d+))?"

    degrees = [1 if d == "" else int(d) for d in re.findall(degree_pattern, polynomial)]

    if any(d == 0 for d in degrees):
        raise ValueError("Use '+1' for the constant term; do not write x^0.")

    degrees.append(0)

    if len(set(degrees)) != len(degrees):
        raise ValueError("Polynomial has duplicate terms.")

    if degrees != sorted(degrees, reverse=True):
        raise ValueError(
            "Polynomial terms must be in descending degree order."
            f"Got degrees {degrees}."
        )

    m = degrees[0]

    if m < 2:
        raise ValueError("Polynomial degree must be >= 2.")
    if degrees[-1] != 0:
        raise ValueError("Polynomial must include constant term '+1'.")
    if len(degrees) < 3:
        raise ValueError(
            "Polynomial must include at least one tap term besides x^m and 1."
        )

    return degrees


def _check_initial_fill(m: int, initial_fill: str) -> str:
    if not re.fullmatch(r"[01]+", initial_fill):
        raise ValueError("Initial fill must be a binary string.")

    if set(initial_fill) == {"0"}:
        raise ValueError("Initial fill must not be all zeros.")

    if len(initial_fill) != m:
        raise ValueError(
            f"Initial fill length must be exactly {m}, got {len(initial_fill)}."
        )

    return initial_fill


def _correlate(x: tuple[int, ...], y: tuple[int, ...]) -> int:
    """Bipolar correlation between two binary sequences.

    Bits are mapped as: 1 -> +1, 0 -> -1.
    Correlation is the sum of products.

    Args:
        x (tuple[int, ...]): _description_
        y (tuple[int, ...]): _description_

    Examples:
        >>> _correlate((1, 0, 1), (1, 0, 1))
        3
        >>> _correlate((1, 0, 1), (0, 1, 0))
        -3

    Returns:
        int: sum([+1 for same bits else -1])
    """
    if len(x) != len(y):
        raise ValueError("Lengths of sequences must be the same.")

    return sum([+1 if xt == yt else -1 for xt, yt in zip(x, y, strict=True)])


def validate_bits(input_bits: BitsLike) -> tuple[int, ...]:
    """Validate input bit sequences.

    Accepted inputs:
      - str: "00101", "0b00101", with optional underscores/spaces
      - int: 101 (interpreted as digit string "101", NOT numeric value 5)
        won't work for any leading zeros (000111 for example.)
      - sequence: explicit bits as 1/0, "0"/"1" or bool.
    """
    if input_bits is None:
        raise ValueError("Input bits cannot be None or empty.")

    try:
        if isinstance(input_bits, int):
            input_bits = list(str(input_bits))
        elif isinstance(input_bits, str):
            input_bits = input_bits.strip().replace(" ", "")
            if input_bits.startswith("0b"):
                input_bits = input_bits[2:]

        bits_list: tuple[int, ...] = tuple(int(bit) for bit in input_bits)

    except (TypeError, ValueError) as e:
        raise TypeError("Bits must be an iterable of 0 and 1 values.") from e

    if any(bit not in (0, 1) for bit in bits_list):
        raise ValueError("Bit sequence must only contain 0 or 1.")

    return bits_list


def binary_to_decimal() -> NoReturn:
    raise NotImplementedError


def decimal_to_binary() -> NoReturn:
    raise NotImplementedError


def berlekamp_massey(bit_sequence: BitsLike) -> list[int]:
    """Compute the Berlekamp–Massey connection polynomial over GF(2).

    Given a binary sequence, this returns the shortest linear recurrence (LFSR)
    that can generate it, expressed as connection polynomial coefficients:

        C = [c0, c1, ..., cL]

    Coefficients are returned in ascending power order (constant-first):

        C(x) = c0 + c1*x + c2*x^2 + ... + cL*x^L

    Notes:
        - This function returns coefficients.
        - The output format will differ from the polynomial format used by MSequence
          (which expects descending degree order like `x^m + x^k + ... + 1`).
          Use `coeffs_to_poly_str()` to convert BM output into this project's format.

    Args:
        bit_sequence (BitsLike): Binary sequence as str, int, list, or tuple.

    Returns:
        list[int]: Connection polynomial coefficients C in ascending power order.
    """
    seq: list[int] = list(validate_bits(bit_sequence))

    C: list[int] = [1]
    B: list[int] = [1]
    L: int = 0
    m: int = -1

    for n in range(len(seq)):
        d: int = seq[n]
        for i in range(1, L + 1):
            if i < len(C):
                d ^= C[i] & seq[n - i]

        if d == 0:
            continue

        T: list[int] = C.copy()
        shift: int = n - m

        c_shift_bits: int = len(B) + shift
        if len(C) < c_shift_bits:
            C.extend([0] * (c_shift_bits - len(C)))

        for j in range(len(B)):
            C[j + shift] ^= B[j]

        if 2 * L <= n:
            L = n + 1 - L
            B = T
            m = n

    C = C[: L + 1]
    return C


def coeffs_to_poly_str(connection_poly: list[int]) -> str:
    """Convert BM connection polynomial coefficients into this project's format.

    BM returns coefficients in ascending power order:

        ```
        C = [c0, c1, ..., cL]
        C(x) = c0 + c1*x + ... + cL*x^L
        ```

    This library represents polynomials in descending
    degree order: `x^m + x^k + ... + 1`

    Mapping used in this project:
        - m = L
        - Always include x^m
        - For each coefficient c_j (j >= 1):
            if c_j == 1, include term x^(m - j)

    Example:
        C = [1, 0, 1, 1]  ->  "x^3+x+1"

    Args:
        C (list[int]): Connection polynomial coefficients from berlekamp_massey().

    Returns:
        str: Polynomial string in descending degree order (e.g. "x^3+x+1").
    """
    m = len(connection_poly) - 1
    degrees = sorted(
        {m} | {m - j for j, cj in enumerate(connection_poly[1:], start=1) if cj == 1},
        reverse=True,
    )

    def term(d: int) -> str:
        return "1" if d == 0 else "x" if d == 1 else f"x^{d}"

    return "+".join(term(d) for d in degrees)


def combine_polys() -> NoReturn:
    raise NotImplementedError


def factorise_polys() -> NoReturn:
    raise NotImplementedError


def primitive_poly_check() -> NoReturn:
    raise NotImplementedError


def recover_fill(polynomial: str, output_bits: BitsLike) -> str:
    """Derive an initial fill (register state) for a Fibonacci LFSR from output bits.

    With this project's convention:
      - output = register[0]
      - register shifts left
    we have: register[0..m-1] == output_bits[0..m-1]

    Args:
        polynomial (str): Polynomial in this project's format (e.g. "x^5+x^2+1")
        output_bits (BitsLike): Output sequence bits (must contain at least m bits)

    Returns:
        str: Initial fill as a bitstring of length m.
    """
    poly = polynomial.replace(" ", "")
    degrees = _validate_polynomial(poly)
    m = degrees[0]

    bits = validate_bits(output_bits)
    if len(bits) < m:
        raise ValueError(f"Need at least {m} output bits to derive initial fill.")

    fill = "".join(str(b) for b in bits[:m])

    return _check_initial_fill(m, fill)


def calculate_canonical_frobenius(
    bits: BitsLike,
) -> tuple[int, list[list[int]], tuple[int, ...]]:
    """Return (shift, cosets, canonical_bits) for Frobenius/squaring canonicalisation.

    We search for the unique LEFT-rotation s such that the rotated sequence b satisfies:
        b[t] == b[(2*t) mod N]  for all t
    where N = len(bits).

    This condition is equivalent to: b is constant on each cyclotomic coset
    generated by repeatedly applying t -> (2t mod N).
    """
    seq: tuple[int, ...] = validate_bits(bits)
    N: int = len(seq)
    if N == 0:
        raise ValueError("Sequence must be non-empty.")

    seen: set[int] = set()
    cosets: list[list[int]] = []

    start = 0
    while start < N:
        if start in seen:
            start += 1
            continue

        coset: list[int] = []
        x = start
        while x not in seen:
            seen.add(x)
            coset.append(x)
            x = (2 * x) % N

        cosets.append(coset)
        start += 1

    cosets.sort(key=lambda c: c[0])

    s = 0
    while s < N:
        i = 0
        ok = True

        while i < len(cosets) and ok:
            c = cosets[i]
            v = seq[(c[0] + s) % N]

            j = 1
            while j < len(c) and seq[(c[j] + s) % N] == v:
                j += 1

            if j != len(c):
                ok = False

            i += 1

        if ok:
            canonical = tuple(seq[(t + s) % N] for t in range(N))
            return s, cosets, canonical

        s += 1

    raise ValueError("No Frobenius-invariant canonical rotation found.")

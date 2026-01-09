import re


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

import pytest

from bseqgen.m_sequence import MSequence


@pytest.fixture
def test_seq_x3() -> MSequence:
    return MSequence("x^3+x+1", "001")


@pytest.mark.parametrize(
    "poly, fill, expected",
    [
        ("x^5 + x^3 + x + 1", "00001", "x^5 + x^3 + x + 1"),
        ("x^3+x+1", "001", "x^3+x+1"),
        ("x^2+x+1", "01", "x^2+x+1"),
    ],
)
def test_self_polynomial(poly: str, fill: str, expected: str) -> None:
    seq = MSequence(poly, fill)
    assert seq.polynomial == expected


@pytest.mark.parametrize(
    "poly, fill, expected",
    [
        ("x^5 + x^3 + x + 1", "00001", [5, 3, 1, 0]),
        ("x^3+x+1", "001", [3, 1, 0]),
        ("x^2+x+1", "01", [2, 1, 0]),
        ("x^4+x^2+1", "0001", [4, 2, 0]),
    ],
)
def test_self_degrees(poly: str, fill: str, expected: list[int]) -> None:
    seq = MSequence(poly, fill)
    assert seq.degrees == expected


@pytest.mark.parametrize(
    "poly, fill",
    [
        ("x^3+x4+1", "001"),  # bad token
        ("x^3+x-1", "001"),  # minus not allowed
        ("x^3+x+1", "000"),  # all-zero fill
        ("x^3+x+1", "01"),  # wrong length
        ("x^3+1", "001"),  # no tap term besides x^m and 1
        ("x^1+x+1", "1"),  # degree too small
        ("x+x^3+1", "001"),  # wrong order
    ],
)
def test_init_rejects_invalid_inputs(poly: str, fill: str) -> None:
    with pytest.raises(ValueError):
        MSequence(poly, fill)

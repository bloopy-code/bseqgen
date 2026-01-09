import pytest

from bseqgen.m_sequence import MSequence


@pytest.fixture
def test_seq_x3() -> MSequence:
    return MSequence("x^3+x+1", "001")


@pytest.mark.parametrize(
    "poly, fill, expected",
    [
        ("x^5 + x^3 + x + 1", "00001", "x^5+x^3+x+1"),
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
        ("x^3+x+1", "01111"),  # wrong length
    ],
)
def test_init_rejects_invalid_inputs(poly: str, fill: str) -> None:
    with pytest.raises(ValueError):
        MSequence(poly, fill)


@pytest.mark.parametrize(
    "poly, fill, expected",
    [
        ("x^5 + x^3 + x + 1", "00001", 5),
        ("x^3+x+1", "001", 3),
        ("x^2+x+1", "01", 2),
        ("x^4+x^2+1", "0001", 4),
    ],
)
def test_self_m(poly: str, fill: str, expected: int) -> None:
    seq = MSequence(poly, fill)
    assert seq.m == expected


@pytest.mark.parametrize(
    "poly, fill, expected",
    [
        ("x^5 + x^3 + x + 1", "00001", [3, 1]),
        ("x^3+x+1", "001", [1]),
        ("x^4+x^2+1", "0001", [2]),
    ],
)
def test_self_tap_degrees(poly: str, fill: str, expected: list[int]) -> None:
    seq = MSequence(poly, fill)
    assert seq.tap_degrees == expected


def test_max_sequence_length(test_seq_x3: MSequence) -> None:
    assert test_seq_x3.max_sequence_length == 7


def test_generate_sequence_x3_x1_1(test_seq_x3: MSequence) -> None:
    out = test_seq_x3.generate_sequence()
    assert out.bit_string == "0010111"


def test_step_updates_register() -> None:
    seq = MSequence("x^3+x+1", "001")
    assert seq.current_register.bit_string == "001"
    assert seq.step() == 0
    assert seq.current_register.bit_string == "010"
    assert seq.step() == 0
    assert seq.current_register.bit_string == "101"


def test_reset_sets_register_and_clears_output() -> None:
    seq = MSequence("x^3+x+1", "001")
    seq.step()
    seq.step()
    assert seq.running_output
    seq.reset()
    assert seq.current_register.bit_string == "001"
    assert seq.running_output == ()


def test_generate_sequence_returns_register_to_seed() -> None:
    seq = MSequence("x^3+x+1", "001")
    seq.generate_sequence()
    assert seq.current_register.bits == seq.initial_fill.bits


def test_generate_k_bits_resets_by_default() -> None:
    seq = MSequence("x^3+x+1", "001")
    out = seq.generate_k_bits(3)  # default reset_on_finish=True
    assert out.bit_string == "001"
    assert seq.current_register.bit_string == "001"
    assert seq.running_output == ()


def test_generate_k_bits_no_reset() -> None:
    seq = MSequence("x^3+x+1", "001")
    out = seq.generate_k_bits(3, reset_on_finish=False)
    assert out.bit_string == "001"
    assert seq.current_register.bit_string == "011"
    assert seq.running_output == (0, 0, 1)


def test_balance_x3() -> None:
    seq = MSequence("x^3+x+1", "001")
    out = seq.generate_sequence()
    assert out.ones == 4
    assert out.zeros == 3

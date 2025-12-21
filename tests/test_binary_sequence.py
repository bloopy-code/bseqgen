from bseqgen.base import BinarySequence
import pytest


@pytest.fixture
def test_seq() -> BinarySequence:
    return BinarySequence((1, 1, 0))


def test_create_sequence_valid() -> None:
    test_sequence = BinarySequence([0, 1, 0])

    assert test_sequence.bits == [0, 1, 0]
    assert test_sequence.length == 3


def test_create_sequence_none() -> None:
    with pytest.raises(ValueError):
        BinarySequence(None)  # type: ignore[arg-type]


def test_create_sequence_empty() -> None:
    with pytest.raises(ValueError):
        BinarySequence([])


def test_create_sequence_string_bin() -> None:
    test_sequence = BinarySequence("1101")

    assert test_sequence.bits == [1, 1, 0, 1]
    assert test_sequence.length == 4


def test_create_sequence_other_values() -> None:
    with pytest.raises(ValueError):
        BinarySequence([3, 8])


def test_create_sequence_tuple() -> None:
    test_sequence = BinarySequence((0, 1, 1))

    assert test_sequence.bits == [0, 1, 1]
    assert test_sequence.length == 3


def test_create_sequence_strlist() -> None:
    test_sequence = BinarySequence(["1", "0"])

    assert test_sequence.bits == [1, 0]
    assert test_sequence.length == 2


def test_bit_string_success(test_seq) -> None:
    assert test_seq.bit_string == "110"


def test_len_matches_length(test_seq) -> None:
    assert len(test_seq) == 3
    assert len(test_seq) == test_seq.length


def test_eq_same_bits() -> None:
    a = BinarySequence((1, 0, 1))
    b = BinarySequence((1, 0, 1))
    assert a == b


def test_eq_diff_bits() -> None:
    a = BinarySequence((1, 0, 1))
    b = BinarySequence((1, 1, 1, 1))
    assert a != b


def test_eq_other_type(test_seq) -> None:
    assert test_seq != [1, 1, 0]
    assert test_seq != "110"


def test_str_long_seq() -> None:
    bits = [1, 0] * 100
    seq = BinarySequence(bits)
    seq_str = str(seq)
    print(seq_str)
    print("..." in seq_str)

    assert seq_str.startswith(seq.bit_string[:32])
    assert seq_str.endswith(seq.bit_string[-32:])


def test_repr_contains_class_and_len(test_seq) -> None:
    r = repr(test_seq)

    assert "BinarySequence" in r
    assert "length=3" in r


def test_as_bytes_len3(test_seq) -> None:
    assert test_seq.as_bytes == b'\x06'


def test_as_bytes_len5() -> None:
    s = BinarySequence((1, 1, 1, 0, 0, 0, 1, 0, 1))
    assert s.as_bytes == b'\x01\xc5'


def test_hex_string(test_seq) -> None:
    assert test_seq.hex_string == '06'


def test_signed(test_seq) -> None:
    assert test_seq.signed == [1, 1, -1]


def test_to_length_truncate() -> None:
    bits = [1] * 100
    seq = BinarySequence(bits)
    assert seq.length == 100

    assert seq.to_length(55).length == 55
    assert seq.to_length(300).length == 300
    assert seq.to_length(1).hex_string == '01'


def test_shift_left(test_seq) -> None:
    assert test_seq.shift(1, 'left') == [1, 0, 1]
    assert test_seq.shift(2) == [0, 1, 1]


def test_shift_right(test_seq) -> None:
    assert test_seq.shift(1, 'right') == [0, 1, 1]

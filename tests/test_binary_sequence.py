from bseqgen.base import BinarySequence
import pytest


@pytest.fixture
def test_seq(): 
    return BinarySequence((1, 1, 0))


def test_create_sequence_valid():
    test_sequence = BinarySequence([0, 1, 0])

    assert test_sequence.bits == [0, 1, 0]
    assert test_sequence.length == 3


def test_create_sequence_none():
    with pytest.raises(ValueError):
        BinarySequence(None)  # type: ignore[arg-type]


def test_create_sequence_empty():
    with pytest.raises(ValueError):
        BinarySequence([])


def test_create_sequence_string_bin():
    test_sequence = BinarySequence("1101")

    assert test_sequence.bits == [1, 1, 0, 1]
    assert test_sequence.length == 4


def test_create_sequence_other_values():
    with pytest.raises(ValueError):
        BinarySequence([3, 8])


def test_create_sequence_tuple():
    test_sequence = BinarySequence((0, 1, 1))

    assert test_sequence.bits == [0, 1, 1]
    assert test_sequence.length == 3


def test_create_sequence_strlist():
    test_sequence = BinarySequence(["1", "0"])

    assert test_sequence.bits == [1, 0]
    assert test_sequence.length == 2


def test_bit_string_success(test_seq):
    assert test_seq.bit_string == "110"


def test_len_matches_length(test_seq):
    assert len(test_seq) == 3
    assert len(test_seq) == test_seq.length


def test_eq_same_bits():
    a = BinarySequence((1, 0, 1))
    b = BinarySequence((1, 0, 1))
    assert a == b


def test_eq_diff_bits():
    a = BinarySequence((1, 0, 1))
    b = BinarySequence((1, 1, 1, 1))
    assert a != b


def test_eq_other_type(test_seq):
    assert test_seq != [1, 1, 0]
    assert test_seq != "110"


def test_str_long_seq():
    bits = [1, 0] * 100
    seq = BinarySequence(bits)
    seq_str = str(seq)
    print(seq_str)
    print("..." in seq_str)

    assert "..." in seq_str
    assert seq_str.startswith(seq.bit_string[:32])
    assert seq_str.endswith(seq.bit_string[-32:])


def test_repr_contains_class_and_len(test_seq):
    r = repr(test_seq)

    assert "BinarySequence" in r
    assert "length=3" in r

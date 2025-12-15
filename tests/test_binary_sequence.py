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


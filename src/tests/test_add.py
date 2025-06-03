"""Tests for the add module."""

from newdotfiles.add import add, multiply


def test_add():
    """Test addition function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(1.5, 2.5) == 4.0


def test_multiply():
    """Test multiplication function."""
    assert multiply(2, 3) == 6
    assert multiply(-1, 1) == -1
    assert multiply(0, 5) == 0
    assert multiply(1.5, 2.0) == 3.0


def test_add_types():
    """Test add function with different types."""
    # Test int + float
    assert add(2, 3.5) == 5.5

    # Test float + int
    assert add(2.5, 3) == 5.5


def test_multiply_types():
    """Test multiply function with different types."""
    # Test int * float
    assert multiply(2, 3.5) == 7.0

    # Test float * int
    assert multiply(2.5, 4) == 10.0

import pytest
import rust_lib


class TestRustLib:
    def test_add_positive_numbers(self):
        assert rust_lib.add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert rust_lib.add(-5, -3) == -8

    def test_add_zero(self):
        assert rust_lib.add(0, 10) == 10

    def test_is_prime_true(self):
        assert rust_lib.is_prime(2) is True
        assert rust_lib.is_prime(7) is True
        assert rust_lib.is_prime(97) is True

    def test_is_prime_false(self):
        assert rust_lib.is_prime(0) is False
        assert rust_lib.is_prime(1) is False
        assert rust_lib.is_prime(4) is False
        assert rust_lib.is_prime(100) is False

    def test_factorial(self):
        assert rust_lib.factorial(0) == 1
        assert rust_lib.factorial(1) == 1
        assert rust_lib.factorial(5) == 120
        assert rust_lib.factorial(10) == 3628800
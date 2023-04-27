# -*- coding: utf-8 -*-
from pikendus_backend.fibo import fibonacci


def test_fibonacci():
    a_prec = 1
    a = 1

    assert fibonacci(0) == a_prec
    assert fibonacci(1) == a
    for n in range(2, 10):
        tmp = a_prec
        a_prec = a
        a = a + tmp
        assert a == fibonacci(n)


if __name__ == "__main__":
    test_fibonacci()

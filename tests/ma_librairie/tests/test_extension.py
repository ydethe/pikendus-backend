from ctypes import addressof

from ma_librairie.item import ITEM
from ma_librairie._ma_librairie import for_func


def test_fortran():
    a = ITEM()
    assert a.i1 == 0

    i = 2
    istat = for_func(i, addressof(a))
    assert istat == 0

    assert a.i1 == i**2 + i**3


if __name__ == "__main__":
    test_fortran()

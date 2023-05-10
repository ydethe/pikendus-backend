# -*- coding: utf-8 -*-
from ma_librairie import get_ma_librairie_version


def test_get_version():
    ver = get_ma_librairie_version()
    assert ver.startswith("0.1")


if __name__ == "__main__":
    test_get_version()

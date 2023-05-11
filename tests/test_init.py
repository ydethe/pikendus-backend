# -*- coding: utf-8 -*-
from pikendus_backend import get_pikendus_backend_version


def test_get_version():
    ver = get_pikendus_backend_version()
    assert isinstance(ver, str)


if __name__ == "__main__":
    test_get_version()

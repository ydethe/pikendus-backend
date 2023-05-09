from ctypes import Structure, c_int


class ITEM(Structure):
    _fields_ = [
        ("i1", c_int),
        ("i2", c_int),
    ]

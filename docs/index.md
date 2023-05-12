# Introduction

pikendus is an estonian word that means 'extension'
pikendus backend is a build backend compliant to [PEP517](https://peps.python.org/pep-0517/). It allows buliding wheel and sdist files, and to compile C and fortran sources into a shared library packed with the wheel file.

# Usage
## Project configuration

Just include the following lines into your pyproject.toml file:

```toml
[build-system]
requires = ["pikendus-backend>=0.2.3"]
build-backend = "pikendus_backend.main"
```

You can finely configure pikendus itself with the following block:

```toml
[tool.pikendus]
c_compiler = "gcc"
f_compiler = "gfortran"
linker = "gcc"
fflags = "-g -Wpadded -Wpacked -Waliasing -Wampersand -Wsurprising -Wintrinsics-std -Wintrinsic-shadow -Wline-truncation -Wreal-q-constant -Wunused -Wunderflow -Warray-temporaries -ffixed-line-length-132 -fcray-pointer -Os -fd-lines-as-comments -mavx -funroll-loops -fexpensive-optimizations -fno-range-check -fbackslash -fimplicit-none"
cflags = "-g -std=gnu99 -Wall"
lflags = ""
structure_description = "data_struct/description.yaml"
```

These are the default options. If you write something else, they will be overriden. Note that the '-fPIC' compilation flag is automatically added, and that the '-shared' linker flag is also automatically added.
The structure_description option is described below.

## Shared structure description

pikendus offers a way of describing shared structures. [See an example](https://gitlab.com/ydethe/pikendus-backend/-/blob/master/tests/ma_librairie/data_struct/description.yaml)

[Example of a shared C structure](example.h.md)

[Example of a shared fortran structure](example.finc.md)

[Example of a shared python structure](example.py.md)

[Example of a python wrapper](wrappers.py.md)

## Fortran coding standard

* Shared [derived types](https://gcc.gnu.org/onlinedocs/gfortran/Derived-Types-and-struct.html) have to be passed by pointer

* Only [cray pointers](https://gcc.gnu.org/onlinedocs/gfortran/Cray-pointers.html) are supported

* Include `pikendus_types.finc` to get the generated derived types working

```fortran
include 'pikendus_types.finc'
```

* If the pattern `"[DEBUG]"` is found in a fortran source, it is replaced on the fly by `"[DEBUG]<nl>@<nf>"`, where nl is the line number and nf the name of the file.

## C coding standard

* Include `pikendus_types.h` to get the generated derived types working

* Shared structures have to be passed by pointer

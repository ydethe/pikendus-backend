# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import List
from numpy.distutils import fcompiler, ccompiler


def liste_fic(root: Path, pattern: str = "**/*", ext: List[str] = ["*"]) -> List[Path]:
    list_fic = []
    found = root.rglob(f"{pattern}.*")
    list_fic.extend((f for f in found if f.is_file() and f.suffix in ext or "*" in ext))

    return list_fic


def build_ext(
    nom: str,
    sig_fic: Path,
    src_dir: Path,
    dst_dir: Path,
):
    "Génération des wrappers python"

    sig_fic = sig_fic.expanduser().resolve()
    src_dir = src_dir.expanduser().resolve()
    dst_dir = dst_dir.expanduser().resolve()

    f2py_path = "f2py --quiet"

    fc = fcompiler.get_default_fcompiler()
    cc = ccompiler.get_default_compiler()

    f77flags = "-fPIC -O0 -fd-lines-as-comments -ffixed-line-length-132 -mavx -fcray-pointer"
    f90flags = f77flags
    cppflags = "-O0"

    l_src_found = liste_fic(root=src_dir, ext=[".f"])
    l_src = list()
    for pth in l_src_found:
        s = str(pth)
        # Suppression de la liste des sources générés par
        # une précédente compilation
        if (
            "fortranobject" not in s
            and not (len(s) >= 8 and s[-8:] == "module.c")
            and "f2pywrappers" not in s
        ):
            l_src.append(s)

    print("Liste des sources à compiler :")
    for fs in l_src:
        print("   %s" % fs)

    # Builds an extension
    f77flags = '"%s %s"' % (cppflags, f77flags)
    f90flags = '"%s %s"' % (cppflags, f90flags)

    inc_dirs = os.popen("python3-config --includes").read().strip().split(" ")
    import numpy

    numpy_inc_dir = Path(numpy.__path__[0]) / "core" / "include"

    # compile extension
    F2pyCommand = []
    F2pyCommand.append(f2py_path + " -c -m %s" % nom)
    F2pyCommand.extend(inc_dirs)
    F2pyCommand.append(f"-I{numpy_inc_dir}")
    F2pyCommand.append("-Isrc")
    F2pyCommand.append("--fcompiler=%s" % fc)
    F2pyCommand.append("--compiler=%s" % cc)
    F2pyCommand.append("--f77flags=%s" % f77flags)
    F2pyCommand.append("--f90flags=%s" % f90flags)
    F2pyCommand.append("%s" % " ".join([str(x) for x in l_src]))
    F2pyCommand.append(str(sig_fic))
    F2pyCommand.append("--build-dir %s" % dst_dir)
    # F2pyCommand.append("2> %s/log_f2py.txt" % dst_dir)
    # F2pyCommand.append(">  %s/log_f2py.txt" % dst_dir)
    F2pyCommand = " ".join(F2pyCommand)
    os.system(F2pyCommand)

    # move files
    lfic = liste_fic(dst_dir, pattern="src.*/**/*", ext=[".f", ".c", ".h"])
    for f in lfic:
        F2pyCommand = "cp %s %s/%s" % (f, dst_dir, f.name)
        os.popen(F2pyCommand)

    # move files
    F2pyCommand = f"rm -rf *.mod *.o *.so {dst_dir}/src.*"
    os.popen(F2pyCommand).read()

    # F2pyCommand = "rm -rf %s/*fortranobject.c" % dst_dir
    # os.popen(F2pyCommand).read()

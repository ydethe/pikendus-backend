# -*- coding: utf-8 -*-

import os
from pathlib import Path
from numpy.distutils import fcompiler, ccompiler
from os.path import relpath, basename


def get_ext(fic: str) -> str:
    ext = fic.split(".")[-1]
    return ext


def liste_fic(root, ext):
    def walk_func(arg, currdir, fnames):
        if ext is not None:
            ext_filtre = ext
            l_fic = [
                x for x in fnames if (ext_filtre == get_ext(x)) and relpath(currdir, root) == "."
            ]
        else:
            l_fic = fnames[:]
        l_fic = [os.path.join(currdir, x) for x in l_fic]
        arg.extend(l_fic)

    list_fic = []
    os.walk(root, walk_func, list_fic)
    return list_fic


def build_ext(
    nom: str,
    sig_fic: Path,
    src_dir: Path,
    dst_dir: Path,
):
    "Génération des wrappers python"
    f2py_path = "f2py --quiet"

    fc = fcompiler.get_default_fcompiler()
    cc = ccompiler.get_default_compiler()

    f77flags = "-fPIC -O0 -fd-lines-as-comments -ffixed-line-length-132 -mavx -fcray-pointer"
    f90flags = f77flags
    cppflags = "-O0"

    l_src = liste_fic(root=src_dir, ext="f")
    for s in l_src:
        # Suppression de la liste des sources des sources C générés par
        # un appel précédent à setup.py
        if "fortranobject" in s:
            l_src.remove(s)
        if len(s) >= 8 and s[-8:] == "module.c":
            l_src.remove(s)
        if "f2pywrappers" in s:
            l_src.remove(s)

    print("Liste des sources à compiler :")
    for fs in l_src:
        print("   %s" % fs)

    # Builds an extension
    f77flags = '"%s %s"' % (cppflags, f77flags)
    f90flags = '"%s %s"' % (cppflags, f90flags)

    # compile extension
    F2pyCommand = []
    F2pyCommand.append(f2py_path + " -c -m %s" % nom)
    F2pyCommand.append("-I/usr/local/include/python2.7/")
    F2pyCommand.append("-I/usr/local/lib/python2.7/site-packages/numpy/core/include/")
    F2pyCommand.append("-Isrc")
    F2pyCommand.append("--fcompiler=%s" % fc)
    F2pyCommand.append("--compiler=%s" % cc)
    F2pyCommand.append("--f77flags=%s" % f77flags)
    F2pyCommand.append("--f90flags=%s" % f90flags)
    F2pyCommand.append("%s" % " ".join(l_src))
    F2pyCommand.append(sig_fic)
    F2pyCommand.append("--build-dir %s" % dst_dir)
    F2pyCommand.append("2> %s/log_f2py.txt" % dst_dir)
    F2pyCommand.append(">  %s/log_f2py.txt" % dst_dir)
    F2pyCommand = " ".join(F2pyCommand)
    os.system(F2pyCommand)

    # move files
    lfic = liste_fic("%s/src.linux-x86_64-2.7/src" % dst_dir, ext=None)
    for f in lfic:
        F2pyCommand = "cp %s %s/%s_%s" % (f, dst_dir, nom, basename(f))
        os.popen(F2pyCommand)

    # move files
    e0 = dst_dir.parts[0]
    F2pyCommand = "rm -rf *.mod *.o *.so %s/src.linux-x86_64-2.7 %s/%s" % (dst_dir, dst_dir, e0)
    os.popen(F2pyCommand).read()

    if "libSysteme" not in nom:
        F2pyCommand = "rm -rf %s/fortranobject.*" % dst_dir
        os.popen(F2pyCommand).read()

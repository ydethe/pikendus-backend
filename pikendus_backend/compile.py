from pathlib import Path
import shutil
import subprocess
import sys
from typing import Dict

import toml
import numpy
import numpy.f2py

from .ligne_debug import ligne_debug


def compile(pdm_build_dir: Path, src_dir: Path) -> Path:
    from . import logger

    build_dir = Path(".pikendus").absolute()
    if build_dir.exists() and not build_dir.is_dir():
        raise AssertionError(f"{build_dir} is not a directory")
    build_dir.mkdir(parents=True, exist_ok=True)

    with open("pyproject.toml", "r") as f:
        config = toml.load(f)

    module_name = config["project"]["name"].replace("-", "_").replace(" ", "_").lower()
    nom = f"_{module_name}"

    preproc_dir = pdm_build_dir / module_name

    if pdm_build_dir.exists() and not pdm_build_dir.is_dir():
        raise AssertionError(f"{pdm_build_dir} is not a directory")
    pdm_build_dir.mkdir(parents=True, exist_ok=True)

    for for_pth in src_dir.rglob("*.f"):
        ligne_debug(for_pth, preproc_dir / for_pth.name)

    for finc_pth in src_dir.rglob("*.finc"):
        dst = pdm_build_dir / finc_pth.name
        if dst.exists():
            dst.unlink()
        shutil.copy(finc_pth, preproc_dir / finc_pth.name)

    for c_pth in src_dir.rglob("*.c"):
        dst = pdm_build_dir / c_pth.name
        if dst.exists():
            dst.unlink()
        shutil.copy(c_pth, preproc_dir / c_pth.name)

    for h_pth in src_dir.rglob("*.h"):
        dst = pdm_build_dir / h_pth.name
        if dst.exists():
            dst.unlink()
        shutil.copy(h_pth, preproc_dir / h_pth.name)

    py_inc_dir = "`python3-config --includes`"
    numpy_inc_dir = numpy.get_include()
    f2py_inc_dir = numpy.f2py.get_include()

    pikendus_cfg: Dict[str, str] = config.get("tool", {"pikendus": dict()})
    c_compiler = pikendus_cfg.get("c_compiler", "gcc")
    f_compiler = pikendus_cfg.get("f_compiler", "gfortran")
    linker = pikendus_cfg.get("linker", "gcc")
    fflags: str = pikendus_cfg.get(
        "fflags",
        "-g -Wpadded -Wpacked -Waliasing -Wampersand -Wsurprising "
        "-Wintrinsics-std -Wintrinsic-shadow -Wline-truncation -Wreal-q-constant "
        "-Wunused -Wunderflow -Warray-temporaries -ffixed-line-length-132 "
        "-fcray-pointer -Os -fd-lines-as-comments -mavx -funroll-loops "
        "-fexpensive-optimizations -fno-range-check -fbackslash -fimplicit-none",
    )
    cflags: str = pikendus_cfg.get("cflags", "-g -std=gnu99 -Wall")
    lflags: str = pikendus_cfg.get("lflags", "")

    fflags += f" -I{pdm_build_dir} {py_inc_dir} -I{numpy_inc_dir} -I{f2py_inc_dir}"
    cflags += f" -I{pdm_build_dir} {py_inc_dir} -I{numpy_inc_dir} -I{f2py_inc_dir}"

    obj_list = []
    for for_pth in preproc_dir.rglob("*.f"):
        obj_pth = build_dir / (for_pth.name + ".o")
        cmd = f"{f_compiler} {fflags} -fPIC -c {for_pth} -o {obj_pth}"
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
            # print(out.stdout.decode("utf-8"))
            logger.info(f"Compiled {for_pth}")
            obj_list.append(str(obj_pth))
        except BaseException:
            logger.error(f"Compilation error for file {for_pth}")

    c_src_files = list(preproc_dir.rglob("*.c"))
    c_src_files.append(Path(numpy.f2py.get_include()) / "fortranobject.c")
    for c_pth in c_src_files:
        obj_pth = build_dir / (c_pth.name + ".o")
        cmd = f"{c_compiler} {cflags} `python3-config --includes` -fPIC -c {c_pth} -o {obj_pth}"
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
            # print(out.stdout.decode("utf-8"))
            logger.info(f"Compiled {c_pth}")
            obj_list.append(str(obj_pth))
        except BaseException:
            logger.error(f"Compilation error for file {c_pth}")

    obj_list_str = " ".join(obj_list)

    impl = sys.implementation
    dll_name = f"{nom}.{impl.cache_tag}-{impl._multiarch}.so"
    dll_pth = preproc_dir / dll_name
    cmd = (
        f"{linker} -o {dll_pth} {obj_list_str}  {lflags} "
        + "`python3-config --ldflags` -lgfortran -shared"
    )
    subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
    logger.info(f"Linked {dll_pth}")

    return dll_pth

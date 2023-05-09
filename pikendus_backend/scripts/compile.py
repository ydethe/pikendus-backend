from pathlib import Path
import shutil
import subprocess

import toml
from numpy.distutils import fcompiler, ccompiler

from .gene_py_src import build_ext
from .ligne_debug import ligne_debug


def compile(build_dir: Path, src_dir: Path, lib_dir: Path) -> Path:
    from .. import logger

    fcompiler.get_default_fcompiler()
    ccompiler.get_default_compiler()

    with open("pyproject.toml", "r") as f:
        config = toml.load(f)

    if build_dir.exists() and not build_dir.is_dir():
        raise AssertionError(f"{build_dir} is not a directory")
    build_dir.mkdir(parents=True, exist_ok=True)

    for for_pth in src_dir.rglob("*.f"):
        ligne_debug(for_pth, build_dir / for_pth.name)

    for finc_pth in src_dir.rglob("*.finc"):
        dst = build_dir / finc_pth.name
        if dst.exists():
            dst.unlink()
        shutil.copy(finc_pth, build_dir)

    for c_pth in src_dir.rglob("*.c"):
        dst = build_dir / c_pth.name
        if dst.exists():
            dst.unlink()
        shutil.copy(c_pth, build_dir)

    for h_pth in src_dir.rglob("*.h"):
        dst = build_dir / h_pth.name
        if dst.exists():
            dst.unlink()
        shutil.copy(h_pth, build_dir)

    pyf_pth = None
    for pyf_pth in src_dir.rglob("*.pyf"):
        pass
    if pyf_pth is None:
        raise AssertionError("pyf file not found")

    module_name = config["project"]["name"].replace("-", "_").replace(" ", "_").lower()

    build_ext(f"_{module_name}", pyf_pth, build_dir, build_dir)

    pikendus_cfg = config.get("tool", {"pikendus": dict()})
    c_compiler = pikendus_cfg.get("c_compiler", "gcc")
    f_compiler = pikendus_cfg.get("f_compiler", "gfortran")
    linker = pikendus_cfg.get("linker", "gcc")
    fflags = pikendus_cfg.get(
        "fflags",
        "-g -Wpadded -Wpacked -Waliasing -Wampersand -Wsurprising "
        "-Wintrinsics-std -Wintrinsic-shadow -Wline-truncation -Wreal-q-constant "
        "-Wunused -Wunderflow -Warray-temporaries -ffixed-line-length-132 "
        "-fcray-pointer -Os -fd-lines-as-comments -mavx -funroll-loops "
        "-fexpensive-optimizations -fno-range-check -fbackslash",
    )
    cflags = pikendus_cfg.get("cflags", "-g -std=gnu99 -Wall -I.")
    lflags = pikendus_cfg.get("lflags", "")

    obj_list = []
    for for_pth in build_dir.rglob("*.f"):
        obj_pth = build_dir / (for_pth.name + ".o")
        cmd = f"{f_compiler} {fflags} -fPIC -c {for_pth} -o {obj_pth}"
        out = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
        print(out.stdout.decode("utf-8"))
        logger.info(f"Compiled {for_pth}")
        obj_list.append(str(obj_pth))

    for c_pth in build_dir.rglob("*.c"):
        obj_pth = build_dir / (c_pth.name + ".o")
        cmd = f"{c_compiler} {cflags} `python3-config --includes` -fPIC -c {c_pth} -o {obj_pth}"
        out = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
        print(out.stdout.decode("utf-8"))
        logger.info(f"Compiled {c_pth}")
        obj_list.append(str(obj_pth))

    obj_list_str = " ".join(obj_list)

    dll_pth = lib_dir / f"_{pyf_pth.stem}.so"
    cmd = (
        f"{linker} -o {dll_pth} {obj_list_str}  {lflags} "
        + "`python3-config --ldflags` -lgfortran -shared"
    )
    out = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
    logger.info(f"Linked {dll_pth}")

    return dll_pth

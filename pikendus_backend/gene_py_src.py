# -*- coding: utf-8 -*-

from pathlib import Path
import subprocess
from typing import List


def liste_fic(root: Path, pattern: str = "**/*", ext: List[str] = ["*"]) -> List[Path]:
    list_fic = []
    found = root.rglob(f"{pattern}.*")
    list_fic.extend((f for f in found if f.is_file() and f.suffix in ext or "*" in ext))

    return list_fic


def generate_wrappers(
    config: dict,
    src_dir: Path,
    pdm_build_dir: Path,
):
    "Génération des wrappers python"
    src_dir = src_dir.expanduser().resolve()
    pdm_build_dir = pdm_build_dir.expanduser().resolve()

    module_name = config["project"]["name"].replace("-", "_").replace(" ", "_").lower()
    nom = f"_{module_name}"

    sig_fic = None
    for sig_fic in src_dir.rglob("*.pyf"):
        pass
    if sig_fic is None:
        raise AssertionError("pyf file not found")

    dst_dir = pdm_build_dir / module_name

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

    # compile extension
    F2pyCommand = []
    F2pyCommand.append(f"f2py --quiet -m {nom}")
    F2pyCommand.extend(l_src)
    F2pyCommand.append(str(sig_fic))
    F2pyCommand.append(f"--build-dir {dst_dir}")
    F2pyCommand = " ".join(F2pyCommand)
    subprocess.run(F2pyCommand, stdout=subprocess.PIPE, shell=True, check=True)

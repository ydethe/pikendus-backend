# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List
import typer

from .pandore_build_system import nom_ver_lib


app = typer.Typer()


@app.command()
def version_module(
    path: List[Path] = typer.Argument(..., help="Chemin vers une ou plusieurs librairie")
):
    """Lecture de la version d'une librairie en copie locale.
    Par exemple, nom_ver_lib ~/Projets/libFichiers retourne libFichiers-5.0 si
    la lib est en version 5.0 dans le build.conf
    """
    for p in path:
        nom, ver = nom_ver_lib(p)
        print(ver)


if __name__ == "__main__":
    app()

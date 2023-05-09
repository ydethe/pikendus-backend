# -*- coding: utf-8 -*-
"""
Main scripts accessible via CLI

"""
import importlib.metadata as im
from pathlib import Path
from typing import List

import typer

from .scripts.ligne_debug import ligne_debug as _ligne_debug
from .scripts.calc_dep_f90 import calc_dep_f90 as _calc_dep_f90
from .scripts.gene_py_src import build_ext as _build_ext
from .scripts.compile import compile as _compile


app = typer.Typer()


def version_callback(value: bool):
    """Print pikendus version string"""
    if value:
        typer.echo(f"Using pikendus in version {im.version('pikendus_backend')}")
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", callback=version_callback),
):
    """Prints the current pikendus version"""
    pass


@app.command()
def ligne_debug(
    src: Path = typer.Argument(..., help="Fichier à transformer"),
    dst: Path = typer.Argument(..., help="Fichier à écrire"),
    debug: bool = typer.Argument(False, help="Mode debug"),
):
    """Transformation des [DEBUG]Message en
    [DEBUG]<nl>@<nf> : Message, où <nl> est le numéro de ligne et <nf> le nom du fichier.
    Créé une copie dans le nême dossier que l'original (extension .old)

    """
    _ligne_debug(src, dst, debug)


@app.command()
def calc_dep_f90(
    dep_dir: Path = typer.Argument(..., help="Dossier des dépendances"),
    obj_dir: Path = typer.Argument(..., help="Dossier des objets"),
    inc_dir: Path = typer.Argument(..., help="Dossier des includes"),
    f: Path = typer.Argument(..., help="Chemin vers un fichier .f"),
    finc_list: List[Path] = typer.Argument(..., help="Liste des .finc à analyser"),
):
    "Résolution des dépendences d'un source f90 en terme de modules"
    _calc_dep_f90(dep_dir, obj_dir, inc_dir, f, finc_list)


@app.command()
def build_ext(
    nom: str = typer.Argument(..., help="Nom de la librairie générée"),
    sig_fic: Path = typer.Argument(..., help="Fichier pyf"),
    src_dir: Path = typer.Argument(..., help="Dossier des sources"),
    dst_dir: Path = typer.Argument(..., help="Dossier où écrire les wrappers"),
):
    "Génération des wrappers python"
    _build_ext(nom, sig_fic, src_dir, dst_dir)


@app.command()
def compile(
    build_dir: Path = typer.Argument(..., help="Dossier de build (temporaire)"),
    src_dir: Path = typer.Argument(..., help="Racine des sources du paquet"),
):
    """Génère un .so à partir de sources fortran ou C"""
    _compile(build_dir, src_dir, src_dir)

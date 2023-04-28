# -*- coding: utf-8 -*-

import os
from pathlib import Path
from types import ModuleType
from typing import TextIO, Tuple
from os.path import abspath, dirname, basename
import imp


def saute_commentaires(file: TextIO) -> str:
    """Cette fonction prend un objet file, et le lit tant qu'elle rencontre des lignes commentees
    Retourne la premiere ligne non commentee.

    Note 1 : Une ligne commentee est une ligne dont le premier caractere est '#' ou ';'
    Note 2 : Un objet file se cree de la maniere suivante : file = codecs.open('mon.fichier', 'r')

    Args:
        file: File object

    Returns:
        Ligne non commentée. A la sortie de cette fonction, le curseur de lecture est
        à la fin de la ligne retournée. A la fin du fichier, renvoi None

    Examples:
        >>> # Creation d'un fichier test (en ecriture avec l'argument 'w')
        >>> import codecs
        >>> file = codecs.open('poney.txt', 'w')
        >>> file.write('# Ceci est un commentaire\\n')
        >>> file.write('1, 2, 3\\n')
        >>> file.write('; Ceci aussi\\n')
        >>> file.close()
        >>> # Ouverture du fichier en lecture (avec l'argument 'r')
        >>> file = codecs.open('poney.txt', 'r')
        >>> saute_commentaires(file)
        '1, 2, 3'
        >>> file.close()
        >>> os.remove('poney.txt')

    """
    line = file.readline()
    if line == "":
        return None
    while line[0] == "#" or line[0] == ";":
        line = file.readline()
        if len(line) == 0:
            return None
    line_ret = line.strip()
    return line_ret


def charge_dll_py(fic: str) -> ModuleType:
    """

    Args:
        fic: Chemin vers le fichier python qui a besoin de sa librairie dynamique correspondante.

    """
    from . import logger

    elem = dirname(abspath(fic)).split("/")
    i = len(elem)
    while True:
        i -= 1
        if i < 0:
            logger.error(f"Impossible de déterminer la librarie dynamique à charger pour {fic}")
            return None
        elif elem[i] == "python":
            break
    lib = elem[i + 1]
    pth = "/".join(elem[:i])
    lib_pth = pth + "/" + lib + ".so"

    res = imp.load_dynamic(lib, lib_pth)

    logger.info(f"Chargement de la lib binaire {res.__file__}")

    return res


def gene_inc_macro_name(fic: str) -> str:
    return basename(fic).replace(".", "_").upper() + "_"


def nom_ver_lib(pth: Path) -> Tuple[str, str]:
    from . import logger

    apth = pth.expanduser().resolve()
    f = open(apth / "app.conf", "r")
    nom = apth.name

    line = f.readline()
    ver = None
    while line != "":
        if "=" in line:
            key, cver = line.strip().split("=")
            if "VERSION" in key:
                ver = cver.strip()
                break
        line = f.readline()

    f.close()

    # On teste si on est dans une copie de travail SVN
    res = os.popen("svn info 2>/dev/null || echo non").read()
    if "non" in res:
        ver = "local"

    if ver == "" or ver is None:
        cmd = "cd %s && svn info" % pth
        res = os.popen(cmd).read().strip()
        info = {}
        for line in res.split("\n"):
            i = line.index(":")
            k = line[:i].strip()
            v = line[i + 1 :].strip()
            info[k] = v
        # Ici, info est un dictionnaire dont les clés sont :
        # 'Path'
        # 'Working Copy Root Path'
        # 'URL'
        # 'Repository Root'
        # 'Repository UUID'
        # 'Revision'
        # 'Node Kind'
        # 'Schedule'
        # 'Last Changed Author'
        # 'Last Changed Rev'
        # 'Last Changed Date'

        if "svn://" not in info["URL"]:
            logger.error(
                "Le motif 'URL: svn://' n'a pas été trouvé dans"
                f"le résultat de la commande '{cmd}'. Obtenu : '{res}'"
            )
            return

        url = info["URL"]

        # On cherche le numéro de révision du dernier commit de la lib,
        # parce que le numéro de révision donné par svn info correspond au numéro de tout le dépôt
        cmd = "svn log -l 1 %s" % url
        res = os.popen(cmd).read().strip()

        if "\n" not in res or "|" not in res:
            logger.error("La commande '%s' a échoué. Obtenu : '%s'" % (cmd, res))
            return

        res = res.split("\n")
        if len(res) < 2:
            logger.error("La commande '%s' a échoué. Obtenu : '%s'" % (cmd, res))
            return

        ver = res[1].split("|")[0].strip()[1:]

    return nom, ver

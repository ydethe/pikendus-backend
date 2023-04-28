# -*- coding: utf-8 -*-

from pathlib import Path
import sys
from os.path import basename
from typing import List


def trouveChaines(line):
    """Voir doc dans libFichiers.atome_ascii"""
    from . import logger

    if line[0] != "'":
        logger.error(
            "Dans les fichiers ASCII, les chaînes de caractères"
            "doivent *commencer* par un gillemet simple"
        )
        return 0, ""

    ind = line.index("'", 1)
    return ind, line[1:ind]


def get_deps_and_mods(filename, finc_list):
    from . import logger

    f = open(filename)

    linc = [basename(x) for x in finc_list]

    if not f:
        logger.error(f"Unable to open {filename}")
        sys.exit(1)

    incs = []
    deps = []
    mods = []
    lines = []
    for lr in f:
        line = lr.strip()
        if "\t" in line and line[:2] != "! " and lr[:2].lower() != "c ":
            sys.stderr.write(
                f"[ATTENTION]Tabulation détectée dans le fichier {filename}."
                "Ceci peut gêner le fonctionnement du build system\n"
            )
        if lines == []:
            lines.append(line)
        else:
            if lr[:6] == "     *":
                lines[-1] = lines[-1] + line[1:]
            else:
                lines.append(line)

    for line in lines:
        if line[:4].lower() == "use ":
            if "only" in line.lower():
                i0 = line.lower().index("only")
                if line[i0 - 1] in [" ", ","] and line[i0 + 4] in [" ", ":"]:
                    line = line[:i0]
            elems = [x.strip().lower() for x in line[4:].split(",")]
            while "" in elems:
                elems.remove("")
            while "iso_c_binding" in elems:
                elems.remove("iso_c_binding")
            deps.extend(map(lambda x: x.strip() + ".mod", elems))
        elif line[:8].lower() == "include ":
            line = line.replace('"', "'")
            ind = line.index("'")
            incs.append(trouveChaines(line[ind:])[1])
        elif line[:7].lower() == "module ":
            mods.append(line[7:].strip().lower() + ".mod")
        else:
            pass

    f.close()

    # Permet de dédoublonner
    deps = set(deps)
    mods = set(mods)
    incs = set(incs)

    # Dans la liste de sincludes en dependance du fichier filename,
    # on ne garde que les includes du dossier source et pas ceux qui viennent d'autres librairires
    incs = incs.intersection(linc)

    # Suppression des dépendances circulaires :
    # si un fichier déclare un module ET l'utilise, on le détecte
    for m in mods:
        while m in deps:
            deps.remove(m)

    return deps, mods, incs


def calc_dep_f90(dep_dir: Path, obj_dir: Path, inc_dir: Path, f: Path, finc_list: List[Path]):
    "Résolution des dépendences d'un source f90 en terme de modules"
    nom = basename(f)[:-2]
    deps, mods, incs = get_deps_and_mods(f, finc_list)
    fic_dep = "%s/%s.d" % (dep_dir, nom)
    line_rel = "%s/%s.os %s:" % (obj_dir, nom, fic_dep)
    if len(deps) > 0:
        sep_obj = " %s/" % obj_dir
        line_rel = line_rel + sep_obj + sep_obj.join(deps)
    if len(incs) > 0:
        sep_inc = " %s/" % inc_dir
        line_rel = line_rel + sep_inc + sep_inc.join(incs)

    if len(deps) > 0 or len(incs) > 0:
        print(line_rel)

    for m in mods:
        mnom = basename(m)[:-4]
        line_rel = "%s/%s.mod: %s/%s.os" % (obj_dir, mnom, obj_dir, nom)
        print(line_rel)

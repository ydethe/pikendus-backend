# -*- coding: utf-8 -*-

import codecs
from os.path import basename
from pathlib import Path


class LigneDebugApp(object):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def traite(self, deb):
        f = codecs.open(self.src, "r", "latin-1")
        g = codecs.open(self.dst, "w", "latin-1")

        nf = basename(self.src)

        balises = ["[DEBUG", "[ERREUR", "[ATTENTION", "[INFO"]

        self.num_line = 1
        self.line = f.readline()
        new_line = self.line
        while self.line != "":
            # Ajout des infos de num de ligne / nom de fichier
            for b in balises:
                lb = len(b)
                if b in new_line:
                    i = new_line.index(b)
                    j = new_line.index("]", i)

                    # Si on a déjà une ligne qui contient les infos de debug, on les met à jour
                    if new_line[j + 1] == "<":
                        k = new_line.index(">", j)
                        new_line = (
                            new_line[: i + lb] + ("]<%.5i@%s" % (self.num_line, nf)) + new_line[k:]
                        )
                    else:
                        new_line = (
                            new_line[: i + lb]
                            + ("]<%.5i@%s>" % (self.num_line, nf))
                            + new_line[j + 1 :]
                        )

            # Suppression de "d" en début de ligne
            if len(new_line) > 0 and new_line[0] == "d":
                if deb:
                    new_line = " " + new_line[1:]
                else:
                    new_line = ""

            g.write(new_line)

            self.line = f.readline()
            new_line = self.line
            self.num_line += 1


def ligne_debug(src: Path, dst: Path, debug: bool = False):
    """Transformation des [DEBUG]Message en
    [DEBUG]<nl>@<nf> : Message, où <nl> est le numéro de ligne et <nf> le nom du fichier.
    Créé une copie dans le nême dossier que l'original (extension .old)

    """
    app = LigneDebugApp(src, dst)

    app.traite(debug)

from pathlib import Path

from pikendus_backend.scripts.gene_py_src import build_ext


def test_build_ext():
    # os.system("rm -rf /home/yannbdt/repos/ma_librairie/build/src/*")

    build_ext(
        nom="ma_librairie",
        sig_fic=Path("ma_librairie.pyf"),
        src_dir=Path("."),
        dst_dir=Path("."),
    )


if __name__ == "__main__":
    test_build_ext()

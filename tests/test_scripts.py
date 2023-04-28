from pathlib import Path
import shutil

from pikendus_backend.scripts.gene_py_src import build_ext


def test_build_ext():
    dst_dir = Path("build/src")
    shutil.rmtree(dst_dir)
    dst_dir.mkdir()

    build_ext(
        nom="libMLFortran",
        sig_fic=Path("ma_librairie/libMLFortran/libMLFortran.pyf"),
        src_dir=Path("ma_librairie/libMLFortran"),
        dst_dir=dst_dir,
    )


if __name__ == "__main__":
    test_build_ext()

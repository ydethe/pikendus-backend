from pathlib import Path
import shutil

from pdm.backend.utils import cd

from pikendus_backend.main import build_wheel, build_sdist


def test_create_wheel():
    rel_build_dir = Path("build")
    with cd("tests/ma_librairie"):
        if rel_build_dir.exists():
            shutil.rmtree(rel_build_dir)

        wheel_directory = Path("dist").absolute()
        build_wheel(wheel_directory=str(wheel_directory))


def test_create_wheel2():
    rel_build_dir = Path("build")
    with cd("tests/ma_librairie_no_struct"):
        if rel_build_dir.exists():
            shutil.rmtree(rel_build_dir)

        wheel_directory = Path("dist").absolute()
        build_wheel(wheel_directory=str(wheel_directory))


def test_create_sdist():
    rel_build_dir = Path("build")
    with cd("tests/ma_librairie"):
        if rel_build_dir.exists():
            shutil.rmtree(rel_build_dir)

        sdist_directory = Path("dist").absolute()
        build_sdist(sdist_directory=str(sdist_directory))


def ntest_generated_lib():
    from ma_librairie.pikendus_types import rectangle
    import ma_librairie.pikendus as p

    r = rectangle()
    p.c_init_rectangle(r, 3, 2)
    area = p.for_area(r)
    print(area)


if __name__ == "__main__":
    # test_create_wheel()
    test_create_wheel2()

from pathlib import Path
import shutil

from pdm.backend.utils import cd

from pikendus_backend.PikendusWheelBuilder import PikendusWheelBuilder


def test_create_wheel():
    rel_build_dir = Path("build")
    with cd("tests/ma_librairie"):
        if rel_build_dir.exists():
            shutil.rmtree(rel_build_dir)

        project = Path(".").absolute()
        wheel_directory = Path("dist").absolute()
        metadata_directory = None
        with PikendusWheelBuilder(project) as builder:
            builder.build(wheel_directory.as_posix(), metadata_directory=metadata_directory)


if __name__ == "__main__":
    test_create_wheel()

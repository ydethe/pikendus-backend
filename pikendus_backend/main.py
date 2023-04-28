import os.path
import pathlib
import tarfile

SDIST_NAME = "mypackage-0.1"
SDIST_FILENAME = SDIST_NAME + ".tar.gz"
WHEEL_FILENAME = "mypackage-0.1-py2.py3-none-any.whl"

#################
# sdist creation
#################


def _exclude_hidden_and_special_files(archive_entry):
    """Tarfile filter to exclude hidden and special files from the archive"""
    if archive_entry.isfile() or archive_entry.isdir():
        if not os.path.basename(archive_entry.name).startswith("."):
            return archive_entry


def _make_sdist(sdist_dir):
    """Make an sdist and return both the Python object and its filename"""
    sdist_path = pathlib.Path(sdist_dir) / SDIST_FILENAME
    sdist = tarfile.open(sdist_path, "w:gz", format=tarfile.PAX_FORMAT)
    # Tar up the whole directory, minus hidden and special files
    sdist.add(os.getcwd(), arcname=SDIST_NAME, filter=_exclude_hidden_and_special_files)
    return sdist, SDIST_FILENAME


def build_sdist(sdist_dir, config_settings):
    """PEP 517 sdist creation hook"""
    sdist, sdist_filename = _make_sdist(sdist_dir)
    return sdist_filename


#################
# wheel creation
#################


def get_requires_for_build_wheel(config_settings):
    """PEP 517 wheel building dependency definition hook"""
    # As a simple static requirement, this could also just be
    # listed in the project's build system dependencies instead
    return ["wheel"]


def build_wheel(wheel_directory, metadata_directory=None, config_settings=None):
    """PEP 517 wheel creation hook"""
    from wheel.archive import archive_wheelfile

    path = os.path.join(wheel_directory, WHEEL_FILENAME)
    archive_wheelfile(path, "src/")
    return WHEEL_FILENAME

# -*- coding: utf-8 -*-
"""

# Testing

## Run the tests

To run tests, just run:

    pdm run pytest

## Test reports

[See test report](../tests/report.html)

[See coverage](../coverage/index.html)

"""
import os
import logging

from rich.logging import RichHandler
from setuptools_scm import get_version  # type: ignore


# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger("ma_librairie_logger")
logger.setLevel(os.environ.get("LOGLEVEL", "INFO").upper())

stream_handler = RichHandler()
logger.addHandler(stream_handler)


def get_ma_librairie_version() -> str:
    """Get the current version of the software:

    For example: '1.0.0'

    Returns:
        The version string

    """
    import importlib.metadata as im

    try:
        # Production mode
        version = im.version("ma_librairie")
    except BaseException:  # pragma: no cover
        version = f"{get_version()} (dev)"

    return version

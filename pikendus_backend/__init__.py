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


class NoDuplicateLogger(logging.Logger):
    def __init__(self, name: str, level=0):
        super().__init__(name, level)
        self.record_lines = []

    def _log(
        self,
        level: int,
        msg: object,
        args,
        exc_info=None,
        extra=None,
        stack_info: bool = False,
        stacklevel: int = 1,
        no_duplicate: bool = False,
    ) -> None:
        if msg not in self.record_lines:
            new_msg = True
            self.record_lines.append(msg)
        else:
            new_msg = False

        if new_msg or not no_duplicate:
            return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


logging.setLoggerClass(NoDuplicateLogger)

# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger("pikendus_backend_logger")
logger.setLevel(os.environ.get("LOGLEVEL", "INFO").upper())

stream_handler = RichHandler()
logger.addHandler(stream_handler)


def get_pikendus_backend_version() -> str:
    """Get the current version of the software:

    For example: '1.0.0'

    Returns:
        The version string

    """
    import importlib.metadata as im

    try:
        # Production mode
        version = im.version("pikendus_backend")
    except BaseException:  # pragma: no cover
        version = f"{get_version()} (dev)"

    return version

from pathlib import Path
from typing import Any, Mapping


__all__ = ["build_wheel", "build_sdist"]


def build_wheel(
    wheel_directory: str,
    config_settings: Mapping[str, Any] = None,
    metadata_directory: str = None,
) -> str:
    """Builds a wheel, places it in wheel_directory"""
    from .PikendusWheelBuilder import PikendusWheelBuilder

    with PikendusWheelBuilder(Path.cwd(), config_settings) as builder:
        return builder.build(wheel_directory, metadata_directory=metadata_directory).name


def build_sdist(sdist_directory: str, config_settings: Mapping[str, Any] = None) -> str:
    """Builds an sdist, places it in sdist_directory"""
    from pdm.backend.sdist import SdistBuilder

    with SdistBuilder(Path.cwd(), config_settings) as builder:
        return builder.build(sdist_directory).name

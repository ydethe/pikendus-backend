from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .PikendusWheelBuilder import (
    PikendusWheelBuilder,
    # PikendusEditableBuilder,
)


def build_wheel(
    wheel_directory: str,
    config_settings: Mapping[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    """Builds a wheel, places it in wheel_directory"""
    with PikendusWheelBuilder(Path.cwd(), config_settings) as builder:
        return builder.build(wheel_directory, metadata_directory=metadata_directory).name


# def build_editable(
#     wheel_directory: str,
#     config_settings: Mapping[str, Any] | None = None,
#     metadata_directory: str | None = None,
# ) -> str:
#     with PikendusEditableBuilder(Path.cwd(), config_settings) as builder:
#         return builder.build(wheel_directory, metadata_directory=metadata_directory).name

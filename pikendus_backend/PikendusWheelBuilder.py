from pathlib import Path
from typing import Iterable

from pdm.backend.hooks import Context
from pdm.backend.wheel import WheelBuilder

from .scripts.compile import compile


class PikendusWheelBuilder(WheelBuilder):
    def get_files(self, context: Context) -> Iterable[tuple[str, Path]]:
        package_dir = self.config.build_config.package_dir
        if package_dir == "":
            src_dir = Path(self.config.data["project"]["name"].replace("-", "_").replace(" ", "_"))
        else:
            src_dir = Path(package_dir)
        compile(build_dir=context.build_dir / "pikendus", src_dir=src_dir, lib_dir=src_dir)
        for relpath, path in super().get_files(context):
            # remove the package-dir part from the relative paths
            if package_dir and relpath.startswith(package_dir + "/"):
                relpath = relpath[len(package_dir) + 1 :]
            yield relpath, path
        yield from self._get_metadata_files(context)


# class PikendusEditableBuilder(PikendusWheelBuilder):
#     target = "editable"
#     hooks = WheelBuilder.hooks + [EditableBuildHook()]

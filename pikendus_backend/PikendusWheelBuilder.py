from pathlib import Path
from typing import Iterable

from pdm.backend.hooks import Context
from pdm.backend.wheel import WheelBuilder

from .scripts.compile import compile


class PikendusWheelBuilder(WheelBuilder):
    def get_files(self, context: Context) -> Iterable[tuple[str, Path]]:
        with open("/home/yannbdt/repos/pikendus_backend/check.log", "w") as log_file:
            package_dir = self.config.build_config.package_dir
            if package_dir == "":
                src_dir = Path(
                    self.config.data["project"]["name"].replace("-", "_").replace(" ", "_")
                )
            else:
                src_dir = Path(package_dir)
            log_file.write(f"package_dir: {src_dir.expanduser().resolve()}\n")
            compile(build_dir=context.build_dir / "pikendus", src_dir=src_dir, lib_dir=src_dir)
            for relpath, path in super().get_files(context):
                # remove the package-dir part from the relative paths
                if package_dir and relpath.startswith(package_dir + "/"):
                    relpath = relpath[len(package_dir) + 1 :]
                log_file.write(f"{relpath}, {path}\n")
                yield relpath, path
        yield from self._get_metadata_files(context)


# class PikendusEditableBuilder(PikendusWheelBuilder):
#     target = "editable"
#     hooks = WheelBuilder.hooks + [EditableBuildHook()]

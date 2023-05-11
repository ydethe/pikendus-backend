from pathlib import Path
from typing import IO, Iterable, Tuple
from importlib.metadata import version as get_version

from pdm.backend.hooks import Context
from pdm.backend.wheel import WheelBuilder

from .structure import generateTypeHeaders, generateFunctionHeaders
from .scripts.compile import compile
from .scripts.gene_py_src import generate_wrappers


class PikendusWheelBuilder(WheelBuilder):
    """Wheel builder

    Args:
        context: the build context

    """

    def get_files(self, context: Context) -> Iterable[Tuple[str, Path]]:
        package_dir = self.config.build_config.package_dir

        if package_dir == "":
            src_dir = self.location / self.config.data["project"]["name"].replace("-", "_").replace(
                " ", "_"
            )
        else:
            src_dir = self.location / package_dir

        for relpath, path in super().get_files(context):
            # remove the package-dir part from the relative paths
            if package_dir and relpath.startswith(package_dir + "/"):
                relpath = relpath[len(package_dir) + 1 :]
            yield relpath, path

        module_name = (
            context.config.data["project"]["name"].replace("-", "_").replace(" ", "_").lower()
        )

        tool_config = context.config.data.get("tool", dict())
        pikendus_config = tool_config.get("pikendus", dict())
        structure_description = pikendus_config.get(
            "structure_description", "data_struct/description.yaml"
        )
        type_files = generateTypeHeaders(
            root=Path(structure_description),
            out_file=context.build_dir / module_name / "pikendus_types",
        )
        for file in type_files:
            yield file.relative_to(context.build_dir).as_posix(), file

        generate_wrappers(context.config.data, src_dir, context.build_dir)

        dll_path = compile(pdm_build_dir=context.build_dir, src_dir=src_dir)
        yield dll_path.absolute().relative_to(context.build_dir).as_posix(), dll_path

        file_pth = generateFunctionHeaders(
            build_dir=context.build_dir,
            root=Path(structure_description),
            type_files=type_files + [dll_path],
            pkg_name=module_name,
            out_file=context.build_dir / module_name / "pikendus.py",
        )
        yield file_pth.relative_to(context.build_dir).as_posix(), file_pth

        yield from self._get_metadata_files(context)

    def _write_wheel_file(self, fp: IO[str], is_purelib: bool) -> None:
        WHEEL_FILE_FORMAT = """\
Wheel-Version: 1.0
Generator: pikendus-backend ({version})
Root-Is-Purelib: {is_purelib}
Tag: {tag}
"""

        try:
            version = get_version("pikendus-backend")
        except ModuleNotFoundError:
            version = "0.0.0+local"

        fp.write(
            WHEEL_FILE_FORMAT.format(
                is_purelib=str(is_purelib).lower(), tag=self.tag, version=version
            )
        )


# class PikendusEditableBuilder(PikendusWheelBuilder):
#     target = "editable"
#     hooks = WheelBuilder.hooks + [EditableBuildHook()]

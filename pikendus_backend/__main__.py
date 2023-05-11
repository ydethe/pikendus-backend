from pathlib import Path
import tempfile

import typer

from .structure import generateFunctionHeaders, generateTypeHeaders


app = typer.Typer()


@app.command()
def gen_includes(
    desc: Path = typer.Argument(..., help="Description file"),
    stem: Path = typer.Argument(..., help="Stem of the destination files"),
    markdown: bool = typer.Option(False, help="Embed the code into a markdown file"),
):
    """Generates includes for the shared data structures"""
    generateTypeHeaders(root=desc, out_file=stem, markdown=markdown)


@app.command()
def gen_wrappers(
    desc: Path = typer.Argument(..., help="Description file"),
    pkg_name: str = typer.Argument(..., help="Name of the package"),
    dest: Path = typer.Argument(
        ..., help="Path to the file where the python wrappers will be written"
    ),
    markdown: bool = typer.Option(False, help="Embed the code into a markdown file"),
):
    """Generates includes for the wrapped functions"""
    tmpd = tempfile.TemporaryDirectory()
    type_files = generateTypeHeaders(root=desc, out_file=Path(tmpd.name) / pkg_name / "temp_types")
    type_files.append(Path(pkg_name + ".so"))
    generateFunctionHeaders(
        build_dir=Path(tmpd.name),
        root=desc,
        type_files=type_files,
        pkg_name=pkg_name,
        out_file=dest,
        markdown=markdown,
    )
    tmpd.cleanup()

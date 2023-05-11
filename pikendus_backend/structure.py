from pathlib import Path
from typing import List
import yaml

import networkx as nx
from networkx.algorithms.dag import topological_sort


_itf_types_map = {
    "u1": "int",
    "u2": "int",
    "u4": "int",
    "u8": "int",
    "s1": "int",
    "s2": "int",
    "s4": "int",
    "s8": "int",
    "f4": "float",
    "f8": "float",
}

_py_types_map = {
    "u1": "ctypes.c_uint8",
    "u2": "ctypes.c_uint16",
    "u4": "ctypes.c_uint32",
    "u8": "ctypes.c_uint64",
    "s1": "ctypes.c_int8",
    "s2": "ctypes.c_int16",
    "s4": "ctypes.c_int32",
    "s8": "ctypes.c_int64",
    "f4": "ctypes.c_float",
    "f8": "ctypes.c_double",
}

_c_types_map = {
    "u1": "uint8_t",
    "u2": "uint16_t",
    "u4": "uint32_t",
    "u8": "uint64_t",
    "s1": "int8_t",
    "s2": "int16_t",
    "s4": "int32_t",
    "s8": "int64_t",
    "f4": "float",
    "f8": "double",
}

_f_types_map = {
    "u1": "integer*1",
    "u2": "integer*2",
    "u4": "integer*4",
    "u8": "integer*8",
    "s1": "integer*1",
    "s2": "integer*2",
    "s4": "integer*4",
    "s8": "integer*8",
    "f4": "real*4",
    "f8": "real*8",
}


class Field(object):
    def __init__(self, name: str, typ: str, niter: int, unit: str, description: str):
        self.name = name
        self.typ = typ
        self.niter = niter
        self.unit = unit
        self.descrption = description

    def isBasicType(self) -> bool:
        return self.typ in _c_types_map.keys()

    def toCType(self) -> str:
        if self.isBasicType():
            ctyp = _c_types_map[self.typ]
        else:
            ctyp = self.typ

        if self.niter == 1:
            return "    %s %s;" % (ctyp, self.name)
        else:
            return "    %s %s[%i];" % (ctyp, self.name, self.niter)

    def toFType(self) -> str:
        if self.isBasicType():
            ctyp = _f_types_map[self.typ]
        else:
            ctyp = "type(%s)" % self.typ

        if self.niter == 1:
            return "         %s :: %s" % (ctyp, self.name)
        else:
            return "         %s :: %s(0:%i)" % (ctyp, self.name, self.niter - 1)

    def toPyType(self) -> str:
        if self.isBasicType():
            ctyp = "%s" % _py_types_map[self.typ]
        else:
            ctyp = self.typ

        if self.niter == 1:
            return '        ("%s", %s),' % (self.name, ctyp)
        else:
            return '        ("%s", %s*%i),' % (self.name, ctyp, self.niter)


class DataStructure(object):
    def __init__(self, name: str):
        self.name = name
        self.fields = []
        self.deps = []

    def addField(self, name: str, typ: str, niter: int, unit: str, description: str) -> Field:
        field = Field(name, typ, int(niter), unit, description)
        self.fields.append(field)
        if not field.isBasicType():
            self.deps.append(field)
        return field

    def toCHeader(self) -> str:
        res = ["typedef struct"]
        res.append("{")
        for f in self.fields:
            res.append(f.toCType())
        res.append("} %s;" % self.name)
        return "\n".join(res)

    def toFHeader(self) -> str:
        res = ["      type %s" % self.name]
        f: Field
        for f in self.fields:
            res.append(f.toFType())
        res.append("      end type %s" % self.name)
        return "\n".join(res)

    def toPyHeader(self) -> str:
        res = ["class %s(ctypes.Structure):" % self.name]
        res.append("    _fields_ = [")
        for f in self.fields:
            res.append(f.toPyType())
        res.append("    ]")
        return "\n".join(res)

    @classmethod
    def fromDict(cls, ds_name: str, data: dict) -> "DataStructure":
        ds = cls(ds_name)
        for field in data["fields"]:
            name = field.get("name")
            typ = field.get("type")
            niter = field.get("niter", 1)
            unit = field.get("unit", "")
            description = field.get("description", "")

            ds.addField(name, typ, int(niter), unit, description)

        return ds


def generateTypeHeaders(root: Path, out_file: Path, markdown: bool = False) -> List[Path]:
    created_files = []

    out_dir = out_file.parent
    out_dir.mkdir(exist_ok=True, parents=True)

    G = nx.DiGraph()
    with open(root, "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    for ds_name in data["types"].keys():
        type_desc = data["types"][ds_name]
        ds = DataStructure.fromDict(ds_name, type_desc)

        G.add_node(ds.name, ds=ds)
        for dep in ds.deps:
            G.add_edge(dep.typ, ds.name)

    list_ds = list(topological_sort(G))

    # Generation header C
    fn = out_file.stem
    macro_name = "_%s_H_" % fn.upper()
    if markdown:
        res = ["```c"]
    else:
        res = []
    res.extend([f"// {out_file}.h", "", "#include <stdint.h>", "", ""])
    res.append("#ifndef %s" % macro_name)
    res.append("#define %s" % macro_name)
    res.append("")
    for ds in list_ds:
        res.append(G.nodes[ds]["ds"].toCHeader())
        res.append("")
    res.append("#endif")
    res.append("")

    if markdown:
        res.append("```")

    h_file = f"{out_file}.h"
    if markdown:
        h_file += ".md"

    with open(h_file, "w") as f:
        f.write("\n".join(res))
        created_files.append(Path(h_file))

    # Generation header Fortran
    if markdown:
        res = ["```fortran"]
    else:
        res = []
    res.append(f"! {out_file}.finc")
    res.append("")
    for ds in list_ds:
        res.append(G.nodes[ds]["ds"].toFHeader())
        res.append("")

    if markdown:
        res.append("```")

    finc_file = f"{out_file}.finc"
    if markdown:
        finc_file += ".md"

    with open(finc_file, "w") as f:
        f.write("\n".join(res))
        created_files.append(Path(finc_file))

    # Generation header Python
    if markdown:
        res = ["```python"]
    else:
        res = []
    res.append(f"# {out_file}.py")
    res.append("")
    res.extend(["import ctypes", "", ""])
    for ds in list_ds:
        res.append(G.nodes[ds]["ds"].toPyHeader())
        res.append("")

    if markdown:
        res.append("```")

    py_file = f"{out_file}.py"
    if markdown:
        py_file += ".md"

    with open(py_file, "w") as f:
        f.write("\n".join(res))
        created_files.append(Path(py_file))

    return created_files


def descToPython(build_dir: Path, dat: dict, pkg_name: str, type_files: List[Path]) -> str:
    code = ["import ctypes"]
    code.append("from ctypes import byref, addressof")
    code.append("import os")
    code.append("from importlib import import_module")

    func_code = f"""\
def _resource_path(resource: str) -> str:
    module = import_module("{pkg_name}")
    spec = module.__spec__

    for root in spec.submodule_search_locations:
        path = os.path.join(root, resource)
        if os.path.exists(path):
            path = path.replace("\\\\", "/")
            if path[1] == ":":
                path = "/%s/%s" % (path[0].lower(), path[3:])
            return path

    raise FileExistsError(resource)
"""

    for file in type_files:
        if file.suffix == ".py":
            m = file.relative_to(build_dir / pkg_name)
            ms = str(m)
            ms = ms.replace(".py", "")
            elem = ms.split("/")
            code.append("")
            code.append(f"from {'.'+'.'.join(elem[:-1] )} import {elem[0] }")
        elif file.suffix == ".so":
            dll_name = file.name

    code.append("")
    code.append("")

    code.append(func_code)

    code.append("")

    for fname in dat.keys():
        # Building function declaration line,
        # and parsing arguments
        # -------------------------------
        line_def = """def %s(""" % fname
        l_arg_in = []
        for arg in dat[fname]["arguments"]:
            if arg["intent"] == "in":
                if arg["type"] in _itf_types_map.keys():
                    typ = _itf_types_map[arg["type"]]
                    ctyp = _py_types_map[arg["type"]]
                    byref = False
                else:
                    typ = f"""{ms}.{arg["type"]}"""
                    ctyp = ""
                    byref = True
                line_def += f"""{arg["name"]}: {typ}, """
                l_arg_in.append((arg, ctyp, byref))

        l_out = []
        l_arg_out = []
        for arg in dat[fname]["arguments"]:
            if arg["intent"] == "out":
                if arg["type"] in _itf_types_map.keys():
                    typ = _itf_types_map[arg["type"]]
                    ctyp = _py_types_map[arg["type"]]
                    create = False
                else:
                    typ = arg["type"]
                    ctyp = arg["type"]
                    create = True
                l_out.append(typ)
                l_arg_out.append((arg, typ, ctyp, create))

        if len(l_out) == 0:
            line_def = line_def[:-2] + "):"
        elif len(l_out) == 1:
            line_def = line_def[:-2] + ") -> %s:" % l_out[0]
        else:
            line_def = line_def[:-2] + ") -> Tuple[%s]:" % (", ".join(l_out))
        code.append(line_def)

        # Building the docstring
        # ----------------------
        code.append(f"""    '''{dat[fname]["help"]}""")
        code.append("")

        if len(l_arg_in) > 0:
            code.append("    Args:")

            for arg, typ, byref in l_arg_in:
                line = f"""        {arg['name'] }: {arg['help']}"""
                if "unit" in arg.keys():
                    line += f" ({arg['unit']})"
                code.append(line)

            code.append("")

        if len(l_arg_out) > 0:
            code.append("    Returns:")

            for arg, typ, ctyp, create in l_arg_out:
                line = f"""        {arg['name'] }: {arg['help']}"""
                if "unit" in arg.keys():
                    line += f" ({arg['unit']})"
                code.append(line)

            code.append("")

        code.append("""    '''""")

        # Binary library importation
        # --------------------------
        if dat[fname]["langage"] == "C":
            code.append(f"""    lib_pth = _resource_path("{dll_name}")""")
            code.append("    lib = ctypes.cdll.LoadLibrary(lib_pth)")
        elif dat[fname]["langage"] == "F":
            code.append(f"""    lib = import_module("{pkg_name}._{pkg_name}")""")

        # Building local variables
        # -------------------------------
        if dat[fname]["langage"] == "C":
            for arg, typ, byref in l_arg_in:
                code.append("""    itf_%s = %s(%s)""" % (arg["name"], typ, arg["name"]))

            for arg, typ, ctyp, create in l_arg_out:
                code.append("""    itf_%s = %s()""" % (arg["name"], ctyp))

        # Calling the compiled function
        # -------------------------------
        if dat[fname]["langage"] == "C":
            line_call = "    res = lib.%s(" % fname
        elif dat[fname]["langage"] == "F":
            line_call = "    res"
            for arg, typ, ctyp, create in l_arg_out:
                line_call += f", {arg['name']}"
            line_call += f" = lib.{fname}("

        for arg, typ, byref in l_arg_in:
            if byref and dat[fname]["langage"] == "F":
                line_call += "addressof(%s), " % arg["name"]
            elif byref and dat[fname]["langage"] == "C":
                line_call += "byref(itf_%s), " % arg["name"]
            elif not byref and dat[fname]["langage"] == "F":
                line_call += "%s, " % arg["name"]
            elif not byref and dat[fname]["langage"] == "C":
                line_call += "itf_%s, " % arg["name"]

        if dat[fname]["langage"] == "C":
            for arg, typ, ctyp, create in l_arg_out:
                line_call += "byref(itf_%s), " % arg["name"]

        line_call = line_call[:-2] + ")"
        code.append(line_call)

        # Handling return code
        # -------------------------------
        code.append("    if res != 0:")
        code.append("        raise ValueError(res)")

        # Building return statement
        # -------------------------------
        if len(l_arg_out) != 0:
            line_ret = "    return "

            for arg, typ, ctyp, create in l_arg_out:
                if create and dat[fname]["langage"] == "C":
                    line_ret += "itf_%s, " % arg["name"]
                elif not create and dat[fname]["langage"] == "C":
                    line_ret += "itf_%s.value, " % arg["name"]
                elif dat[fname]["langage"] == "F":
                    line_ret += "%s, " % arg["name"]

            code.append(line_ret[:-2])

        code.append("")
        code.append("")

    return "\n".join(code)


def generateFunctionHeaders(
    build_dir: Path,
    root: Path,
    type_files: List[Path],
    pkg_name: str,
    out_file: Path,
    markdown: bool = False,
) -> Path:
    with open(root, "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    code = descToPython(build_dir, data["functions"], pkg_name, type_files)
    if markdown:
        out_file = out_file.parent / (out_file.name + ".md")
    with open(out_file, "w") as f:
        if markdown:
            f.write("```python\n")
        f.write(code)
        if markdown:
            f.write("\n```")

    return out_file.absolute()


if __name__ == "__main__":
    type_files = generateTypeHeaders(
        Path("tests/ma_librairie/data_struct/description.yaml"),
        out_file=Path("tests/ma_librairie/build/ma_librairie/pikendus_types"),
    )
    type_files.append(
        Path("tests/ma_librairie/build/ma_librairie/_ma_librairie.cpython-310-x86_64-linux-gnu.so")
    )

    generateFunctionHeaders(
        build_dir=Path("tests/ma_librairie/build"),
        root=Path("tests/ma_librairie/data_struct/description.yaml"),
        type_files=type_files,
        pkg_name="ma_librairie",
        out_file=Path("tests/ma_librairie/build/ma_librairie/pikendus.py"),
    )

import os
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
    def fromFile(cls, file: str) -> str:
        with open(file, "r") as f:
            lines = f.readlines()

        fn = os.path.basename(file)
        ds_name, _ = os.path.splitext(fn)
        ds = cls(ds_name)
        for line in lines:
            if line.startswith("#"):
                continue
            elems = line.strip().split(",")
            if len(elems) != 5:
                break

            name, typ, niter, unit, description = [x.strip() for x in elems]

            ds.addField(name, typ, int(niter), unit, description)

        return ds


def generateTypeHeaders(root: Path, out_file: Path) -> List[Path]:
    created_files = []

    out_dir = out_file.parent
    out_dir.mkdir(exist_ok=True, parents=True)

    G = nx.DiGraph()
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            _, ext = os.path.splitext(f)
            if ext != ".ds":
                continue

            ds = DataStructure.fromFile(os.path.join(dirpath, f))
            G.add_node(ds.name, ds=ds)
            for dep in ds.deps:
                G.add_edge(dep.typ, ds.name)

    list_ds = list(topological_sort(G))

    # Generation header C
    fn = out_file.stem
    macro_name = "_%s_H_" % fn.upper()
    res = [f"// {out_file}.h", "", "#include <stdint.h>", "", ""]
    res.append("#ifndef %s" % macro_name)
    res.append("#define %s" % macro_name)
    res.append("")
    for ds in list_ds:
        res.append(G.nodes[ds]["ds"].toCHeader())
        res.append("")
    res.append("#endif")
    res.append("")

    with open(f"{out_file}.h", "w") as f:
        f.write("\n".join(res))
        created_files.append(Path(f"{out_file}.h"))

    # Generation header Fortran
    res = [f"! {out_file}.finc"]
    res.append("")
    for ds in list_ds:
        res.append(G.nodes[ds]["ds"].toFHeader())
        res.append("")

    with open(f"{out_file}.finc", "w") as f:
        f.write("\n".join(res))
        created_files.append(Path(f"{out_file}.finc"))

    # Generation header Python
    res = [f"# {out_file}.py"]
    res.append("")
    res.extend(["import ctypes", "", ""])
    for ds in list_ds:
        res.append(G.nodes[ds]["ds"].toPyHeader())
        res.append("")

    with open(f"{out_file}.py", "w") as f:
        f.write("\n".join(res))
        created_files.append(Path(f"{out_file}.py"))

    return created_files


def loadFunctionDescription(fic: str) -> dict:
    with open(fic, "r") as f:
        dat = yaml.load(f, Loader=yaml.SafeLoader)
    return dat


def descToPython(dat: dict, pkg_name: str) -> str:
    code = ["import ctypes"]
    code.append("from ctypes import byref")
    code.append("from %s.include.%s_ds import *" % (pkg_name, pkg_name))
    code.append("""lib = ctypes.cdll.LoadLibrary("./%s/_%s.so")""" % (pkg_name, pkg_name))

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
                    typ = arg["type"]
                    ctyp = ""
                    byref = True
                line_def += "%s: %s, " % (arg["name"], typ)
                l_arg_in.append((arg["name"], ctyp, byref))

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
                l_arg_out.append((arg["name"], typ, ctyp, create))

        if len(l_out) == 0:
            line_def = line_def[:-2] + "):"
        elif len(l_out) == 1:
            line_def = line_def[:-2] + ") -> %s:" % l_out[0]
        else:
            line_def = line_def[:-2] + ") -> Tuple[%s]:" % (", ".join(l_out))
        code.append(line_def)
        code.append("    '''%s'''" % dat[fname]["help"])

        # Building local variables
        # -------------------------------
        for arg, typ, byref in l_arg_in:
            code.append("""    itf_%s = %s(%s)""" % (arg, typ, arg))

        for arg, typ, ctyp, create in l_arg_out:
            code.append("""    itf_%s = %s()""" % (arg, ctyp))

        # Calling the compiled function
        # -------------------------------
        if dat[fname]["langage"] == "F":
            line_call = "    res=lib.%s_(" % fname
        elif dat[fname]["langage"] == "C":
            line_call = "    res=lib.%s(" % fname
        else:
            raise ValueError(dat[fname]["langage"])

        for arg, typ, byref in l_arg_in:
            if byref:
                line_call += "byref(itf_%s), " % arg
            else:
                line_call += "itf_%s, " % arg

        for arg, typ, ctyp, create in l_arg_out:
            line_call += "byref(itf_%s), " % arg

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
                if create:
                    line_ret += "itf_%s, " % arg
                else:
                    line_ret += "itf_%s.value, " % arg

            code.append(line_ret[:-2])

        code.append("")

    return "\n".join(code)


def generateFunctionHeaders(root: str, pkg_name: str, out_file: str):
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            _, ext = os.path.splitext(f)
            if ext != ".fd":
                continue

            fd_pth = os.path.join(dirpath, f)
            fcts = loadFunctionDescription(fd_pth)
            code = descToPython(fcts, pkg_name)
            f = open(out_file, "w")
            f.write(code)
            f.close()


if __name__ == "__main__":
    generateTypeHeaders(
        "/home/yannbdt/repos/ma_librairie/ma_librairie/data_struct",
        out_file="/home/yannbdt/repos/ma_librairie/build/pikendus/test",
    )

    # generateFunctionHeaders(
    #     "pyFramework/data_struct",
    #     pkg_name="pyFramework",
    #     out_file="pyFramework/pyFramework.py",
    # )

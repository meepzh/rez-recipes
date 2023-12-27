import collections.abc


name = "maya"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.PATH.append("{this._bin_path}")


description = (
    "Professional 3D software for creating realistic characters and blockbuster-worthy "
    "effects."
)


external = True


@early()
def requires():
    requires = []

    python_ver = this._exec_mayapy(
        "requires",
        ["import platform", "print(platform.python_version())"],
        initialize=False,
    )
    requires.append(f"~python-{python_ver}")

    pyside2_ver = this._exec_mayapy(
        "requires",
        ["import PySide2", "print(PySide2.__version__)"],
        initialize=False,
    )
    requires.append(f"~PySide2-{pyside2_ver}")

    return requires


@early()
def tools():
    tools = [
        "BatchRenderWrapper",
        "FurRenderer",
        "Render",
        "blur2d",
        "cgc",
        "cgfx",
        "cginfo",
        "dispatch_maya_render",
        "fcheck",
        "filePaste",
        "fileStats",
        "imgcvt",
        "imgdiff",
        "interlace",
        "mayald",
        "mayapy",
        "senddmp",
    ]

    major = this.__version.partition(".")[0]
    tools.append(f"maya{major}")

    return tools


uuid = "recipes.maya.native"


variants = [["platform-**", "arch-**", "os-**"]]


@early()
def version():
    return this.__version + "-native"


_native = True


def __bin_path() -> str:
    """Determines Maya's binaries path.

    Returns:
        The path.
    """
    import pathlib
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command("_bin_path", ["pacman", "-Ql", "maya"])
    except FileNotFoundError:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError("Cannot determine '_bin_path' without 'pacman'")
    else:
        for path in out.split("\n"):
            if path.endswith("bin/mayapy"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)


def _exec_mayapy(
    attr: str, src: collections.abc.Iterable[str] | str, initialize: bool = True
) -> str:
    """Uses mayapy to determine a package attribute.

    Args:
        attr: The name of the package attribute.
        src: Lines of Python code to execute.
        initialize: Loads the Maya libraries.

    Returns:
        The computed value.
    """
    import pathlib
    import subprocess

    if isinstance(src, str):
        src = [src]
    else:
        src = list(src)

    if initialize:
        src = ["import maya.standalone", "maya.standalone.initialize()"] + src

    mayapy_bin = pathlib.Path(_bin_path, "mayapy")
    proc = subprocess.Popen(
        [mayapy_bin, "-c", "; ".join(src)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()

    if proc.returncode:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError(
            f"Error determining package attribute '{attr}':\n{err}"
        )

    return out.strip()


def _version() -> str:
    """Determines Maya's version string.

    Returns:
        The version.
    """
    out = _exec_mayapy(
        "version",
        [
            "from maya import cmds",
            (
                "print(f"
                "'{cmds.about(majorVersion=True)}"
                ".{cmds.about(minorVersion=True)}"
                ".{cmds.about(cutIdentifier=True)}')"
            ),
        ],
    )
    return out.rpartition("\n")[2]


_bin_path = __bin_path()
__version = _version()

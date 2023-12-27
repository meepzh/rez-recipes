import maya_packaging


name = "maya"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.PATH.append("{this._bin_path}")

    # https://groups.google.com/g/rez-config/c/2IWclNTJEk0/m/MGAA-ZB-BwAJ
    env.PYTHON_EXE = "mayapy"


description = (
    "Professional 3D software for creating realistic characters and blockbuster-worthy "
    "effects."
)


external = True


@early()
def requires():
    requires = []

    python_ver = maya_packaging.exec_mayapy(
        "requires",
        ["import platform", "print(platform.python_version())"],
        this._bin_path,
        initialize=False,
    )
    requires.append(f"~python-{python_ver}-_maya")

    pyside2_ver = maya_packaging.exec_mayapy(
        "requires",
        ["import PySide2", "print(PySide2.__version__)"],
        this._bin_path,
        initialize=False,
    )
    requires.append(f"~PySide2-{pyside2_ver}-_maya")

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


def _version() -> str:
    """Determines Maya's version string.

    Returns:
        The version.
    """
    out = maya_packaging.exec_mayapy(
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
        _bin_path,
    )
    return out.rpartition("\n")[2]


_bin_path = maya_packaging.bin_path()
__version = _version()

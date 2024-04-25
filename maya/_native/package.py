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


has_plugins = True


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
    import pathlib
    from rez.system import system

    potential_tools = [
        "BatchRenderWrapper",
        "FieldAssembler",
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
        "mayabatch",
        "mayald",
        "mayapy",
        "quicktimeShim",
        "senddmp",
        "xpm2bmp",
    ]

    # Add variations of the Maya executable
    major = this.__version.partition(".")[0]
    potential_tools.append(f"maya{major}")
    potential_tools.append("maya")

    # Filter for tools that actually exist
    bin_path = pathlib.Path(this._bin_path)
    suffix = ".exe" if system.platform == "windows" else ""

    tools_ = []
    for tool in potential_tools:
        test_path = bin_path.joinpath(tool).with_suffix(suffix)
        if test_path.is_file():
            tools_.append(tool)

    return tools_


uuid = "recipes.maya"


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


_bin_path = maya_packaging.get_bin_path()
__version = _version()

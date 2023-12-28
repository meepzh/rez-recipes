import maya_packaging


name = "PySide2"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.QT_PREFERRED_BINDING = "PySide2"


description = "Dummy package for Maya's internal PySide2 installation."


external = True


@early()
def requires():
    return [this.__maya_package.qualified_name]


@early()
def tools():
    import pathlib

    tools = []

    for child in pathlib.Path(__maya_package._bin_path).iterdir():
        if child.stem.startswith("pyside"):
            tools.append(child.stem)

    return tools


uuid = "recipes.PySide2"


variants = [["platform-**", "arch-**", "os-**"]]


@early()
def version():
    # As an internal installation, this should take lower priority when resolving
    # PySide2
    return this.__version + "-_maya"


_native = True


def _version() -> str:
    """Determines the version of Maya's internal PySide2 installation.

    Returns:
        The version.
    """
    return maya_packaging.exec_mayapy(
        "_version",
        ["import PySide2", "print(PySide2.__version__)"],
        __maya_package._bin_path,
        initialize=False,
    )


__maya_package = maya_packaging.latest_existing_package()
__version = _version()

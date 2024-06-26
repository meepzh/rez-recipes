name = "PySide2"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.QT_PREFERRED_BINDING = "PySide2"

    if building and this._cmake_path:
        env.CMAKE_MODULE_PATH.append("{this._cmake_path}")


description = (
    "The official Python module from the Qt for Python project, which provides access "
    "to the complete Qt 5.12+ framework."
)


external = True


@early()
def requires():
    return ["Qt-" + this.__version]


uuid = "recipes.PySide2"


@early()
def variants():
    from rez.package_py_utils import find_site_python

    python_pkg = find_site_python("PySide2")
    return [
        [
            "platform-**",
            "arch-**",
            "os-**",
            f"python-{python_pkg.version.rpartition('.')[0]}",
        ]
    ]


@early()
def version():
    return this.__version + "-native"


_native = True


@early()
def _cmake_path() -> str | None:
    """Determines PySide2's CMake module path.

    Returns:
        The path, if found.
    """
    import pathlib
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command(
            "_cmake_path", ["pacman", "--query", "--list", "pyside2"]
        )
    except FileNotFoundError:
        pass
    else:
        for path in out.split("\n"):
            if path.endswith("PySide2Config.cmake"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)

    return None


def _version() -> str:
    """Determines PySide2's version string.

    Returns:
        The version.
    """
    from rez.package_py_utils import exec_python

    return exec_python("version", ["import PySide2", "print(PySide2.__version__)"])


__version = _version()

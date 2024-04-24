name = "python"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.PATH.append("{this._bin_path}")

    # https://groups.google.com/g/rez-config/c/2IWclNTJEk0/m/MGAA-ZB-BwAJ
    env.PYTHON_EXE = "python"

    if building and hasattr(this, "_cmake_path"):
        env.CMAKE_MODULE_PATH.append("{this._cmake_path}")


description = (
    "An interpreted, object-oriented, high-level programming language with dynamic "
    "semantics."
)


external = True


@early()
def tools():
    return (
        _generate_tools_from_pacman()
        or _generate_tools_from_bin_path()
        or _generate_default_tools()
    )


uuid = "recipes.python"


variants = [["platform-**", "arch-**", "os-**"]]


@early()
def version():
    return this.__version + "-native"


_native = True


def __bin_path() -> str:
    """Determines Python's binaries path.

    Returns:
        The path.
    """
    from rez.package_py_utils import exec_python

    return exec_python(
        "_bin_path",
        ["import pathlib", "import sys", "print(pathlib.Path(sys.executable).parent)"],
    )


@early()
def _cmake_path() -> str | None:
    """Determines Python's CMake module path.

    Returns:
        The path, if found.
    """
    import pathlib
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command("_cmake_path", ["pacman", "--query", "--list", "cmake"])
    except FileNotFoundError:
        pass
    else:
        for path in out.split("\n"):
            if path.endswith("FindPython.cmake"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)

    return None


def _generate_default_tools() -> list[str]:
    """Generates a default list of Python tools based on the Python version.

    Returns:
        The tool names.
    """
    py_major, py_minor, _ = __version.split(".")
    tools_ = ["2to3", f"2to3-{py_major}.{py_minor}"]
    for version_ in (
        "",
        py_major,
        f"{py_major}.{py_minor}",
    ):
        for tool in (
            "idle",
            "pydoc",
            "python",
        ):
            tools_.append(f"{tool}{version_}")
    return tools_


def _generate_tools_from_bin_path() -> list[str] | None:
    """Determines a list of Python tools from the bin path in which a typical Windows
    Python installation is expected to be found.

    Returns:
        The tool names, if any were found.
    """
    from itertools import chain
    import pathlib

    install_root = pathlib.Path(_bin_path)
    tools_: list[str] = []
    for tool in chain(
        install_root.glob("*.exe"), install_root.joinpath("Scripts").glob("*.exe")
    ):
        tools_.append(tool.stem)
    return tools_


def _generate_tools_from_pacman() -> list[str] | None:
    """Determines a list of Python tools from the pacman package manager.

    Returns:
        The tool names, if any were found.
    """
    from rez.package_py_utils import exec_command

    tools_: list[str] = []

    try:
        out, err = exec_command("tools", ["pacman", "--query", "--list", "python"])
    except FileNotFoundError:
        return None

    for path in out.split("\n"):
        if not path.startswith("python /usr/bin"):
            continue
        tool = path.rpartition("/")[2]
        if tool:
            tools_.append(tool)

    return tools_


@early()
def _site_paths():
    """See `rez.package_py_utils.find_site_python <https://rez.readthedocs.io/en/stable/api/rez.package_py_utils.html#rez.package_py_utils.find_site_python>`_."""
    import ast
    from rez.package_py_utils import exec_python

    paths_literal = exec_python(
        "_site_paths", ["import site", "print(site.getsitepackages())"]
    )
    return ast.literal_eval(paths_literal)


def _version() -> str:
    """Determines Python's version string.

    Returns:
        The version.
    """
    from rez.package_py_utils import exec_python

    return exec_python(
        "version", ["import platform", "print(platform.python_version())"]
    )


_bin_path = __bin_path()
__version = _version()

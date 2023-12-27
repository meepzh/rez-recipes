name = "python"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.PATH.append("{this._bin_path}")

    # https://groups.google.com/g/rez-config/c/2IWclNTJEk0/m/MGAA-ZB-BwAJ
    env.PYTHON_EXE = "python"

    if building and this._cmake_path:
        env.CMAKE_MODULE_PATH.append("{this._cmake_path}")


description = (
    "An interpreted, object-oriented, high-level programming language with dynamic "
    "semantics."
)


external = True


@early()
def tools():
    from rez.package_py_utils import exec_command

    tools = []

    try:
        out, err = exec_command("tools", ["pacman", "-Ql", "python"])
    except FileNotFoundError:
        py_major, py_minor, _ = this.__version.split(".")
        tools = ["2to3", f"2to3-{py_major}.{py_minor}"]
        for version in (
            "",
            py_major,
            f"{py_major}.{py_minor}",
        ):
            for tool in (
                "idle",
                "pydoc",
                "python",
            ):
                tools.append(f"{tool}{version}")
    else:
        for path in out.split("\n"):
            if not path.startswith("python /usr/bin"):
                continue
            tool = path.rpartition("/")[2]
            if tool:
                tools.append(tool)

    return tools


uuid = "recipes.python.native"


variants = [["platform-**", "arch-**", "os-**"]]


@early()
def version():
    return this.__version + "-native"


_native = True


@early()
def _bin_path() -> str:
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
def _cmake_path() -> str:
    """Determines Python's CMake module path.

    Returns:
        The path.
    """
    import pathlib
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command("tools", ["pacman", "-Ql", "cmake"])
    except FileNotFoundError:
        return None
    else:
        for path in out.split("\n"):
            if path.endswith("FindPython.cmake"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)


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


__version = _version()

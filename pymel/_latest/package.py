import pathlib

import maya_packaging


name = "pymel"


authors = ["Robert Zhou"]


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.append("{root}/{this._site_path}")


description = "Python in Maya Done Right"


external = True


requires = ["maya-2020+<2025"]


tools = ["ipymel"]


uuid = "recipes.pymel"


@early()
def variants():
    return [[f"python-{this.__python_version.rpartition('.')[0]}"]]


@early()
def version():
    from rez.package_py_utils import exec_command

    out, err = exec_command(
        "version", [__mayapy_path, "-m", "pip", "index", "versions", "pymel"]
    )
    return out.partition("(")[2].partition(")")[0]


def _python_version() -> str:
    """Determines the Python version being used.

    Returns:
        The version.
    """
    return maya_packaging.exec_mayapy(
        "requires",
        ["import platform", "print(platform.python_version())"],
        __maya_package._bin_path,
        initialize=False,
    )


@early()
def _site_path() -> str:
    """Caches the site-packages path relative to the installation directory.

    Returns:
        The path.
    """
    return str(
        pathlib.Path(
            "lib", f"python{this.__python_version.rpartition('.')[0]}", "site-packages"
        )
    )


__maya_package = maya_packaging.latest_existing_package()
__mayapy_path = str(pathlib.Path(__maya_package._bin_path, "mayapy"))
__python_version = _python_version()

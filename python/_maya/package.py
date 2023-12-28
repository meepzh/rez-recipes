import maya_packaging


name = "python"


authors = ["Robert Zhou"]


build_command = False


description = "Dummy package for Maya's internal Python installation."


external = True


@early()
def requires():
    return [this.__maya_package.qualified_name]


uuid = "recipes.python"


variants = [["platform-**", "arch-**", "os-**"]]


@early()
def version():
    # As an internal installation, this should take lower priority when resolving Python
    return this.__version + "-_maya"


_native = True


@early()
def _site_paths():
    """See `rez.package_py_utils.find_site_python <https://rez.readthedocs.io/en/stable/api/rez.package_py_utils.html#rez.package_py_utils.find_site_python>`_."""
    import ast

    paths_literal = maya_packaging.exec_mayapy(
        "_site_paths",
        ["import site", "print(site.getsitepackages())"],
        __maya_package._bin_path,
        initialize=False,
    )
    return ast.literal_eval(paths_literal)


def _version() -> str:
    """Determines the version of Maya's internal Python installation.

    Returns:
        The version.
    """
    return maya_packaging.exec_mayapy(
        "_version",
        ["import platform", "print(platform.python_version())"],
        __maya_package._bin_path,
        initialize=False,
    )


__maya_package = maya_packaging.latest_existing_package()
__version = _version()

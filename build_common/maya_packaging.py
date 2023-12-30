"""Common code for packaging Maya.
"""
from collections.abc import Iterable
import pathlib
import subprocess

from rez.packages import (
    Package,
    iter_packages,
)
from rez.package_order import SortedOrder
from rez.package_py_utils import exec_command


def bin_path() -> str:
    """Determines Maya's binaries path.

    Returns:
        The path.
    """
    try:
        out, err = exec_command("bin_path", ["pacman", "-Ql", "maya"])
    except FileNotFoundError:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError("Cannot determine 'bin_path' without 'pacman'")
    else:
        for path in out.split("\n"):
            if path.endswith("bin/mayapy"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)


def exec_mayapy(
    attr: str,
    src: Iterable[str] | str,
    cached_bin_path: str = None,
    initialize: bool = True,
) -> str:
    """Uses mayapy to determine a package attribute.

    Args:
        attr: The name of the package attribute.
        src: Lines of Python code to execute.
        cached_bin_path: The bin path of the mayapy executable to reuse.
        initialize: Loads the Maya libraries.

    Returns:
        The computed value.
    """
    if isinstance(src, str):
        src = [src]
    else:
        src = list(src)

    if initialize:
        src = ["import maya.standalone", "maya.standalone.initialize()"] + src

    cached_bin_path = cached_bin_path or bin_path()

    mayapy_bin = pathlib.Path(cached_bin_path, "mayapy")
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


def get_python_version(cached_bin_path: str = None) -> str:
    """Determines the version of Maya's internal Python installation.

    Args:
        cached_bin_path: The bin path of the mayapy executable to reuse.

    Returns:
        The version.
    """
    cached_bin_path = cached_bin_path or bin_path()

    return exec_mayapy(
        "_version",
        ["import platform", "print(platform.python_version())"],
        cached_bin_path,
        initialize=False,
    )


def latest_existing_package() -> Package:
    """Searches the installed Rez packages for the highest Maya package installation
    with an installation that exists on disk.

    Returns:
        The Maya package.
    """
    packages = []
    for package in iter_packages("maya"):
        bin_path = getattr(package, "_bin_path", None)
        if bin_path and pathlib.Path(bin_path).is_dir():
            packages.append(package)

    if not packages:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError(
            "Could not find a 'maya' package with an installation that exists on disk"
        )

    packages = SortedOrder(descending=True).reorder(packages)
    return packages[0]

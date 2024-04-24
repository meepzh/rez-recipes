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

    Raises:
        InvalidPackageError: When the bin path cannot be determined.

    Returns:
        The path.
    """
    path = _get_bin_path_from_pacman() or _get_bin_path_from_winreg()

    if not path:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError("Could not determine Maya's bin path")

    return path


def exec_mayapy(
    attr: str,
    src: Iterable[str] | str,
    cached_bin_path: str = "",
    initialize: bool = True,
) -> str:
    """Uses mayapy to determine a package attribute.

    Args:
        attr: The name of the package attribute.
        src: Lines of Python code to execute.
        cached_bin_path: The bin path of the mayapy executable to reuse.
        initialize: Loads the Maya libraries.

    Raises:
        InvalidPackageError: When mayapy returns an error code.

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


def get_python_version(cached_bin_path: str = "") -> str:
    """Determines the version of Maya's internal Python installation.

    Args:
        cached_bin_path: The bin path of the mayapy executable to reuse.

    Raises:
        InvalidPackageError: When mayapy returns an error code.

    Returns:
        The version.
    """
    cached_bin_path = cached_bin_path or bin_path()

    return exec_mayapy(
        "python_version",
        ["import platform", "print(platform.python_version())"],
        cached_bin_path,
        initialize=False,
    )


def latest_existing_package() -> Package:
    """Searches the installed Rez packages for the highest Maya package installation
    with an installation that exists on disk.

    Raises:
        InvalidPackageError: When the ``maya`` package cannot be found.

    Returns:
        The Maya package.
    """
    packages = []
    for package in iter_packages("maya"):
        bin_path_ = getattr(package, "_bin_path", None)
        if bin_path_ and pathlib.Path(bin_path_).is_dir():
            packages.append(package)

    if not packages:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError(
            "Could not find a 'maya' package with an installation that exists on disk"
        )

    packages = SortedOrder(descending=True).reorder(packages)
    return packages[0]


def _get_bin_path_from_pacman() -> str | None:
    """Determines Maya's binaries path from the pacman package manager.

    Returns:
        The path, if found.
    """
    try:
        out, err = exec_command("bin_path", ["pacman", "--query", "--list", "maya"])
    except FileNotFoundError:
        pass
    else:
        for path in out.split("\n"):
            if path.endswith("bin/mayapy"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)

    return None


def _get_bin_path_from_winreg() -> str | None:
    """Determines Maya's binaries path from the Windows registry.

    Returns:
        The path, if found.
    """
    try:
        import winreg
    except ModuleNotFoundError:
        return None

    with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Autodesk\Maya"
    ) as maya_key:
        # Iterate through the sub-keys to determine the highest Maya installation year
        key_count, _, _ = winreg.QueryInfoKey(maya_key)
        max_year = ""
        for index in range(key_count):
            year = winreg.EnumKey(maya_key, index)
            if year.isdigit() and year > max_year:
                max_year = year

        if not max_year:
            return None

        with winreg.OpenKey(
            maya_key, max_year + r"\Setup\InstallPath"
        ) as install_path_key:
            value, _ = winreg.QueryValueEx(install_path_key, "MAYA_INSTALL_LOCATION")

    return str(pathlib.Path(value, "bin"))

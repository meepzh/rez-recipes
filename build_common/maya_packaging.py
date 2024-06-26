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

    cached_bin_path = cached_bin_path or get_bin_path()

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


def get_bin_path() -> str:
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


def get_PySide_module(cached_bin_path: str = "") -> str:
    """Determines the module name of Maya's internal PySide installation.

    Args:
        cached_bin_path: The bin path of the mayapy executable to reuse.

    Raises:
        InvalidPackageError: When mayapy returns an error code.

    Returns:
        The name.
    """
    cached_bin_path = cached_bin_path or get_bin_path()

    return exec_mayapy(
        "PySide_module",
        [
            "import importlib.util",
            "print('PySide2') if importlib.util.find_spec('PySide2') else None",
            "print('PySide6') if importlib.util.find_spec('PySide6') else None",
        ],
        cached_bin_path,
        initialize=False,
    )


def get_PySide_version(PySide_module: str = "", cached_bin_path: str = "") -> str:
    """Determines the version of Maya's internal PySide installation.

    Args:
        PySide_module: The name of the module to retrieve a version for. If not
            provided, then the name will be automatically determined.
        cached_bin_path: The bin path of the mayapy executable to reuse.

    Raises:
        InvalidPackageError: When mayapy returns an error code.

    Returns:
        The version.
    """
    PySide_module = PySide_module or get_PySide_module()
    cached_bin_path = cached_bin_path or get_bin_path()

    return exec_mayapy(
        "PySide_version",
        [f"import {PySide_module}", f"print({PySide_module}.__version__)"],
        cached_bin_path,
        initialize=False,
    )


def get_python_version(cached_bin_path: str = "") -> str:
    """Determines the version of Maya's internal Python installation.

    Args:
        cached_bin_path: The bin path of the mayapy executable to reuse.

    Raises:
        InvalidPackageError: When mayapy returns an error code.

    Returns:
        The version.
    """
    cached_bin_path = cached_bin_path or get_bin_path()

    return exec_mayapy(
        "python_version",
        ["import platform", "print(platform.python_version())"],
        cached_bin_path,
        initialize=False,
    )


def get_Qt_version(cached_bin_path: str = "") -> str:
    """Determines the version of Maya's internal Qt installation.

    Args:
        cached_bin_path: The path to search for Qt binaries.

    Raises:
        InvalidPackageError: When the version can't be determined.

    Returns:
        The version.
    """
    import re
    from rez.exceptions import InvalidPackageError
    from rez.system import system

    cached_bin_path = cached_bin_path or get_bin_path()
    suffix = ".exe" if system.platform == "windows" else ""

    qt_bin_path = pathlib.Path(cached_bin_path).joinpath("qmake").with_suffix(suffix)
    search_pattern = r"Qt version (\d+\.\d+\.\d+)"
    bin_args = ["-v"]

    if not qt_bin_path.exists():
        qt_bin_path = qt_bin_path.parent.joinpath("qtdiag").with_suffix(suffix)
        search_pattern = r"Qt (\d+\.\d+\.\d+)"
        bin_args = []

    if not qt_bin_path.exists():
        raise InvalidPackageError(
            f"Could not find Qt in Maya bin path: {cached_bin_path}"
        )

    out, err = exec_command("version", [str(qt_bin_path)] + bin_args)
    matches = re.search(search_pattern, out)
    if matches:
        return matches.groups(1)[0]

    raise InvalidPackageError(f"Could not determine Qt's version string: {out}")


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

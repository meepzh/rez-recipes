name = "unreal_engine"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.PATH.append("{this._bin_path}")


description = (
    "A complete suite of real-time 3D tools made by developers, for developers."
)


external = True


has_plugins = True


@early()
def tools():
    import pathlib
    from rez.system import system

    bin_path = pathlib.Path(this._bin_path)
    suffix = ".exe" if system.platform == "windows" else ""

    tools_ = []
    for child in bin_path.glob("*"):
        if not child.is_file():
            continue
        if suffix == child.suffix:
            tools_.append(child.stem)

    return tools_


uuid = "recipes.unreal_engine"


variants = [["platform-**", "arch-**", "os-**"]]


@early()
def version():
    version_ = _get_version_from_pacman()

    if not version_:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError("Could not determine Unreal Engine's version string")

    return version_ + "-native"


_native = True


def __bin_path() -> str:
    """Determines Unreal Engine's binaries path.

    Raises:
        InvalidPackageError: When the bin path cannot be determined.

    Returns:
        The path.
    """
    path = _get_bin_path_from_pacman()

    if not path:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError("Could not determine Unreal Engine's bin path")

    return path


def _get_bin_path_from_pacman() -> str | None:
    """Determines Unreal Engine's binaries path from the pacman package manager.

    Returns:
        The path, if found.
    """
    import pathlib
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command(
            "bin_path", ["pacman", "--query", "--list", "unreal-engine"]
        )
    except FileNotFoundError:
        pass
    else:
        for path in out.split("\n"):
            if path.endswith("UnrealEditor") and "Saved" not in path:
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)

    return None


def _get_version_from_pacman() -> str | None:
    """Determines Unreal Engine's version from the pacman package manager.

    Returns:
        The version, if found.
    """
    import re
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command(
            "version", ["pacman", "--query", "--info", "unreal-engine"]
        )
    except FileNotFoundError:
        pass
    else:
        matches = re.search(r"Version[\s:]+(\d+\.\d+\.\d+)", out)
        if matches:
            return matches.groups(1)[0]

    return None


_bin_path = __bin_path()

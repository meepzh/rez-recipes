"""To make use of this recipe, please provide a path to the SHAPES zip file using the
SHAPES_DOWNLOAD CMake variable.
"""
import typing

import maya_packaging


name = "SHAPES"


authors = ["Robert Zhou"]


def commands():
    env.MAYA_MODULE_PATH.append("{root}")


description = "The versatile blend shape editor for Autodesk Maya"


external = True


plugin_for = ["maya"]


requires = ["maya-2020+"]


uuid = "recipes.shapes"


@early()
def variants():
    return [
        [
            "platform-**",
            "arch-**",
            "maya-*",
            f"python-{this.__python_version.rpartition('.')[0]}",
        ]
    ]


@early()
def version():
    from rez.exceptions import InvalidPackageError

    version = _find_version_from_build()
    if not version:
        version = _find_version_from_args()
    if version:
        return version

    raise InvalidPackageError("Could not find a version number to use from versions.md")


def _extract_version_from_md(md_file: typing.IO) -> str | None:
    """Searches the versions.md file for the first version string it can find.

    Returns:
        The version, if found.
    """
    import re

    version_pattern = re.compile(r"\b\d+\.\d+\.\d+\b")

    for line in md_file:
        match = version_pattern.search(str(line))
        if match:
            return match.group(0)

    return None


def _find_version_from_args() -> str | None:
    """Searches the arguments to rez-build for the SHAPES download to extract and search
    for version information.

    Returns:
        The version, if found.
    """
    import pathlib
    import re
    import sys

    download_path = ""
    variable_pattern = re.compile(r"-DSHAPES_DOWNLOAD(:\w+)?=(.*)")
    for arg in sys.argv:
        match = variable_pattern.search(arg)
        if match:
            download_path = match.group(2) or download_path

    if download_path:
        from zipfile import ZipFile

        with ZipFile(download_path) as download_file:
            with download_file.open(
                str(pathlib.Path("SHAPES", "versions.md"))
            ) as versions_file:
                return _extract_version_from_md(versions_file)

    return None


def _find_version_from_build() -> str | None:
    """Searches the build directory for version information on SHAPES.

    Returns:
        The version, if found.
    """
    import os
    import pathlib

    versions_path = ""
    for dirpath, dirnames, filenames in os.walk("build"):
        if "versions.md" in filenames:
            versions_path = pathlib.Path(dirpath, "versions.md")

    if versions_path:
        with open(versions_path) as versions_file:
            return _extract_version_from_md(versions_file)

    return None


__python_version = maya_packaging.get_python_version()

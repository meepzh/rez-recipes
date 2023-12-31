"""To make use of this recipe, please provide a path to the SHAPES zip file using the
SHAPES_DOWNLOAD CMake variable.
"""
import maya_packaging


name = "SHAPES"


authors = ["Robert Zhou"]


def commands():
    env.MAYA_MODULE_PATH.append("{root}")


description = "The versatile blend shape editor for Autodesk Maya"


external = True


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
    import os
    import pathlib
    import re
    from rez.exceptions import InvalidPackageError

    versions_path = None
    for dirpath, dirnames, filenames in os.walk("build"):
        if "versions.md" in filenames:
            versions_path = pathlib.Path(dirpath, "versions.md")

    if not versions_path:
        raise InvalidPackageError(
            "Could not find the build directory versions.md file required for "
            "determining the version number"
        )

    version_pattern = re.compile(r"\b\d+\.\d+\.\d+\b")

    with open(versions_path) as versions_file:
        for line in versions_file:
            match = version_pattern.search(line)
            if match:
                return match.group(0)

    raise InvalidPackageError("Could not find a version number to use from versions.md")


__python_version = maya_packaging.get_python_version()

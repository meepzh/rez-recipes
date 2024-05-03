import maya_packaging


name = "PySide"


authors = ["Robert Zhou"]


build_command = False


def commands():
    env.QT_PREFERRED_BINDING = "PySide"


description = "Dummy package for Maya's internal PySide6+ installation."


external = True


hashed_variants = True


@early()
def requires():
    qt_version = ".".join(this.__version.split(".")[:3])  # Strip extra numbers
    return ["Qt-" + qt_version]


uuid = "recipes.PySide6+"


@early()
def variants():
    return [
        [
            "platform-**",
            "arch-**",
            "os-**",
            "maya-**",
            f"python-{this.__python_version.rpartition('.')[0]}",
        ]
    ]


@early()
def version():
    # As an internal installation, this should take lower priority when resolving
    # PySide2
    return this.__version + "-_maya"


_native = True


def _version() -> str:
    """Determines the version of Maya's internal PySide installation.

    Returns:
        The version.
    """
    return maya_packaging.get_PySide_version(cached_bin_path=__maya_package._bin_path)


__maya_package = maya_packaging.latest_existing_package()
__python_version = maya_packaging.get_python_version(
    cached_bin_path=__maya_package._bin_path
)
__version = _version()

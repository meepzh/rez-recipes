import maya_packaging


name = "Qt"


authors = ["Robert Zhou"]


def commands():
    if building:
        env.CMAKE_MODULE_PATH.append("{root}/cmake")


description = (
    "A cross-platform application development framework for creating graphical user "
    "interfaces as well as cross-platform applications."
)


external = True


def pre_build_commands():
    env.QT_CMAKE_TAR_PATH = this._cmake_tar_path


uuid = "recipes.qt"


variants = [["platform-**", "arch-**", "os-**", "maya-**"]]


tools = [
    "moc",
    "qmake",
    "qtpaths",
    "rcc",
    "uic",
]


@early()
def version():
    version_ = maya_packaging.get_Qt_version(cached_bin_path=__maya_bin_path)
    return version_ + "-_maya"


_native = True


@early()
def _cmake_tar_path() -> str:
    """Determines the location of the tarballed Qt5 CMake files.

    Returns:
        The path, if found.
    """
    import pathlib

    cmake_path = pathlib.Path(__maya_bin_path).parent.joinpath("cmake")
    return str(next(cmake_path.glob("*.tar.gz"), ""))


__maya_bin_path = maya_packaging.get_bin_path()

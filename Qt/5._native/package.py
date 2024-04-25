name = "Qt"


authors = ["Robert Zhou"]


build_command = False


def commands():
    if building and this._cmake_path:
        env.CMAKE_MODULE_PATH.append("{this._cmake_path}")


description = (
    "A cross-platform application development framework for creating graphical user "
    "interfaces as well as cross-platform applications."
)


external = True


uuid = "recipes.qt"


variants = [["platform-**", "arch-**", "os-**"]]


@early()
def tools():
    import pathlib
    from rez.system import system

    potential_tools = [
        "assistant",
        "assistant.debug",
        "balsam",
        "balsam.debug",
        "canbusutil",
        "canbusutil.debug",
        "designer",
        "designer.debug",
        "fixqt4headers.pl",
        "lconvert",
        "lconvert.debug",
        "licheck64",
        "linguist",
        "linguist.debug",
        "lprodump",
        "lprodump.debug",
        "lrelease",
        "lrelease-pro",
        "lrelease-pro.debug",
        "lrelease.debug",
        "lupdate",
        "lupdate-pro",
        "lupdate-pro.debug",
        "lupdate.debug",
        "meshdebug",
        "meshdebug.debug",
        "moc",
        "moc.debug",
        "pixeltool",
        "pixeltool.debug",
        "qcollectiongenerator",
        "qcollectiongenerator.debug",
        "qdbus",
        "qdbus.debug",
        "qdbuscpp2xml",
        "qdbuscpp2xml.debug",
        "qdbusviewer",
        "qdbusviewer.debug",
        "qdbusxml2cpp",
        "qdbusxml2cpp.debug",
        "qdistancefieldgenerator",
        "qdistancefieldgenerator.debug",
        "qdoc",
        "qdoc.debug",
        "qgltf",
        "qgltf.debug",
        "qhelpgenerator",
        "qhelpgenerator.debug",
        "qlalr",
        "qlalr.debug",
        "qmake",
        "qml",
        "qml.debug",
        "qmlcachegen",
        "qmlcachegen.debug",
        "qmleasing",
        "qmleasing.debug",
        "qmlformat",
        "qmlformat.debug",
        "qmlimportscanner",
        "qmlimportscanner.debug",
        "qmllint",
        "qmllint.debug",
        "qmlmin",
        "qmlmin.debug",
        "qmlplugindump",
        "qmlplugindump.debug",
        "qmlpreview",
        "qmlpreview.debug",
        "qmlprofiler",
        "qmlprofiler.debug",
        "qmlscene",
        "qmlscene.debug",
        "qmltestrunner",
        "qmltestrunner.debug",
        "qmltyperegistrar",
        "qmltyperegistrar.debug",
        "qscxmlc",
        "qscxmlc.debug",
        "qtattributionsscanner",
        "qtattributionsscanner.debug",
        "qtdiag",
        "qtdiag.debug",
        "qtpaths",
        "qtpaths.debug",
        "qtplugininfo",
        "qtplugininfo.debug",
        "qtwaylandscanner",
        "qtwaylandscanner.debug",
        "qvkgen",
        "qvkgen.debug",
        "qwebengine_convert_dict",
        "qwebengine_convert_dict.debug",
        "rcc",
        "rcc.debug",
        "repc",
        "repc.debug",
        "sdpscanner",
        "sdpscanner.debug",
        "syncqt.pl",
        "tracegen",
        "tracegen.debug",
        "uic",
        "uic.debug",
        "xmlpatterns",
        "xmlpatterns.debug",
        "xmlpatternsvalidator",
        "xmlpatternsvalidator.debug",
    ]

    bin_path = pathlib.Path(_bin_path())
    suffix = ".exe" if system.platform == "windows" else ""

    tools_ = []
    for tool in potential_tools:
        for qualifier in ("", "-qt5"):
            test_path = bin_path.joinpath(tool + qualifier + suffix)
            if test_path.is_file():
                tools_.append(tool + qualifier + suffix)

    return tools_


@early()
def version():
    version_ = _get_version_from_pacman()

    if not version_:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError("Could not determine Qt's version string")

    return version_ + "-native"


_native = True


def _bin_path() -> str:
    """Determines Qt5's primary binaries path.

    Returns:
        The path.
    """
    path = _get_bin_path_from_pacman()

    if not path:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError("Could not determine Qt's bin path")

    return path


@early()
def _cmake_path() -> str | None:
    """Determines Qt5's CMake module path.

    Returns:
        The path, if found.
    """
    import pathlib
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command(
            "_cmake_path", ["pacman", "--query", "--list", "qt5-base"]
        )
    except FileNotFoundError:
        pass
    else:
        for path in out.split("\n"):
            if path.endswith("Qt5Config.cmake"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)

    return None


def _get_bin_path_from_pacman() -> str | None:
    """Determines Qt5's primary binaries path from the pacman package manager.

    Returns:
        The path, if found.
    """
    import pathlib
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command(
            "_cmake_path", ["pacman", "--query", "--list", "qt5-base"]
        )
    except FileNotFoundError:
        pass
    else:
        for path in out.split("\n"):
            if path.endswith("qmake-qt5"):
                path = path.partition(" ")[2]
                return str(pathlib.Path(path).parent)

    return None


def _get_version_from_pacman() -> str | None:
    """Determines Qt5's version from the pacman package manager.

    Returns:
        The version, if found.
    """
    import re
    from rez.package_py_utils import exec_command

    try:
        out, err = exec_command("version", ["pacman", "--query", "--info", "qt5-base"])
    except FileNotFoundError:
        pass
    else:
        matches = re.search(r"Version[\s:]+(\d+\.\d+\.\d+)", out)
        if matches:
            return matches.groups(1)[0]

    return None

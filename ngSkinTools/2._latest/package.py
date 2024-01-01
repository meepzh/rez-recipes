import maya_packaging


name = "ngSkinTools"


authors = ["Robert Zhou"]


def commands():
    env.MAYA_PACKAGE_PATH.append("{root}")


description = (
    "A skinning plugin for Autodesk Maya, introducing new concepts to character "
    "skinning such as layers, any-pose-mirroring, enhanced paint brushes, true "
    "smoothing, and more."
)


external = True


plugin_for = ["maya"]


def pre_build_commands():
    from rez.system import system

    platform = system.platform
    if platform == "osx":
        platform = "macos"

    env.FETCH_URL = (
        f"https://download.ngskintools.com/ngskintools-{this.version}-{platform}.zip"
    )


@early()
def requires():
    import re
    from urllib.request import urlopen

    with urlopen(f"https://www.ngskintools.com/releases/v2/{__version}/") as response:
        html = response.read()

    years = re.findall(r"Maya (\d{4})", str(html))
    years = "|".join(years)
    return [f"maya-{years}"]


uuid = "recipes.ngskintools"


@early()
def variants():
    return [
        [
            "platform-**",
            "maya-*",
            f"python-{this.__python_version.rpartition('.')[0]}",
        ]
    ]


@early()
def version():
    return __version


def _version() -> str:
    """Finds the latest v2 release available.

    Returns:
        The version.
    """
    import re
    from urllib.request import urlopen

    with urlopen("https://www.ngskintools.com/releases/v2/") as response:
        html = response.read()

    match = re.search(r"releases/v2/(2\.\d+\.\d+)/", str(html))
    return match.group(1)


__python_version = maya_packaging.get_python_version()
__version = _version()

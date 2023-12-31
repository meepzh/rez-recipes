import maya_packaging


name = "mGear"


authors = ["Robert Zhou"]


def commands():
    env.MAYA_MODULE_PATH.append("{root}")
    env.MGEAR_MODULE_PATH = "{root}"


description = "Open source rigging and animation framework for Autodesk Maya."


external = True


def pre_build_commands():
    env.FETCH_URL = f"https://github.com/mgear-dev/mgear4/releases/download/{this.version}/mgear_{this.version}.zip"


requires = [
    "maya-2018+",
    "pymel",
]


uuid = "recipes.mgear"


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
    import json
    import re
    from urllib.request import urlopen

    with urlopen("https://api.github.com/repos/mgear-dev/mgear4/tags") as response:
        tag_data = json.load(response)

    valid_tag_pattern = re.compile(r"\d+\.\d+\.\d+$")
    latest_tag = None
    for tag in tag_data:
        if not valid_tag_pattern.match(tag["name"]):
            continue
        tag["version_tuple"] = tuple(tag["name"].split("."))
        if not latest_tag or tag["version_tuple"] > latest_tag["version_tuple"]:
            latest_tag = tag

    if not latest_tag:
        from rez.exceptions import InvalidPackageError

        raise InvalidPackageError(
            "Could not determine the latest version tag for mGear"
        )

    return latest_tag["name"]


__python_version = maya_packaging.get_python_version()

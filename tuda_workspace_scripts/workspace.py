#!/usr/bin/env python3
try:
    from colcon_core.plugin_system import get_package_identification_extensions
except ImportError:
    from colcon_core.package_identification import get_package_identification_extensions
from colcon_core.package_identification import identify, IgnoreLocationException
import os


def get_workspace_root(directory=None):
    """
    :param directory: Directory from which to search the workspace root. If None will try to find from current and if that fails from the COLCON_PREFIX_PATH
    :return: The path to the workspace root or None if no workspace found.
    """
    if directory is None:
        root = get_workspace_root(os.getcwd())
        if root is not None:
            return root
        colcon_prefix_path = os.environ.get("COLCON_PREFIX_PATH", None)
        return (
            get_workspace_root(colcon_prefix_path)
            if colcon_prefix_path is not None
            else None
        )
    if ".ros2_workspace" in os.listdir(directory):
        return directory
    parent = os.path.dirname(directory)
    return None if parent == directory else get_workspace_root(parent)


def find_packages_in_directory(directory):
    packages = []
    identification_extensions = get_package_identification_extensions()
    visited_paths = set()
    for dirpath, dirnames, _ in os.walk(directory, followlinks=True):
        real_dirpath = os.path.realpath(dirpath)
        if real_dirpath in visited_paths:
            del dirnames[:]
            continue
        visited_paths.add(real_dirpath)
        try:
            result = identify(identification_extensions, dirpath)
        except IgnoreLocationException:
            del dirnames[:]
            continue
        if result:
            packages.append(result)
            del dirnames[:]
            continue
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

    return [p.name for p in packages]


def get_packages_in_workspace(workspace_path=None):
    """
    Looks for packages in the src folder of a workspace.
    :param workspace_path: Path to the workspace root (The parent directory of the src folder).
        If None will use get_workspace_root() to try to find it.
    """
    if workspace_path is None:
        workspace_path = get_workspace_root()
        if workspace_path is None:
            return []
    return find_packages_in_directory(os.path.join(workspace_path, "src"))


class PackageChoicesCompleter:
    """
    Looks for packages in the src subdirectory of the workspace located at workspace_path.
    """

    def __init__(self, workspace_path):
        self.workspace_path = workspace_path

    def __call__(self, **kwargs):
        if self.workspace_path is None:
            return []
        return get_packages_in_workspace(self.workspace_path)


if __name__ == "__main__":
    print(get_workspace_root())

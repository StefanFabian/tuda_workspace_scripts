#!/usr/bin/env python3
from ament_index_python import get_packages_with_prefixes
import os


def get_workspace_root(directory=None):
    """
    :param directory: Directory from which to search the workspace root. If None will try to find from current and if
      that fails from the COLCON_PREFIX_PATH
    :return: The path to the workspace root or None if no workspace found
    """
    if directory is None:
        root = get_workspace_root(os.getcwd())
        if root is not None:
            return root
        colcon_prefix_path = os.environ.get('COLCON_PREFIX_PATH', None)
        return get_workspace_root(colcon_prefix_path) if colcon_prefix_path is not None else None
    if '.ros2_workspace' in os.listdir(directory):
        return directory
    parent = os.path.dirname(directory)
    return None if parent == directory else get_workspace_root(parent)


def get_packages_in_workspace(workspace_path=None):
    if workspace_path is None:
        workspace_path = get_workspace_root()
    packages = get_packages_with_prefixes()
    return [name for name in packages if packages[name].startswith(workspace_path)]


class PackageChoicesCompleter:
    def __init__(self, workspace_path):
        self.workspace_path = workspace_path

    def __call__(self, **kwargs):
        if self.workspace_path is None:
            return []
        return get_packages_in_workspace(self.workspace_path)


if __name__ == '__main__':
    print(get_workspace_root())

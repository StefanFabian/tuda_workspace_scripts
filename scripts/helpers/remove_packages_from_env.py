#!/usr/bin/env python
from tuda_workspace_scripts.workspace import get_packages_in_workspace, get_workspace_root
import argparse
import os


def get_ament_prefix_path_without_packages(packages):
    ament_prefix_path = os.environ.get('AMENT_PREFIX_PATH', None)
    if ament_prefix_path is None:
        return None
    paths = ament_prefix_path.split(os.pathsep)
    paths = filter(lambda x: x.split(os.path.sep)[-1] not in packages, paths)
    return os.pathsep.join(paths)


def get_ament_prefix_path_without_workspace(workspace_root):
    ament_prefix_path = os.environ.get('AMENT_PREFIX_PATH', None)
    if ament_prefix_path is None:
        return None
    paths = ament_prefix_path.split(os.pathsep)
    paths = filter(lambda x: not x.startswith(workspace_root), paths)
    return os.pathsep.join(paths)


def get_cmake_prefix_path_without_packages(packages):
    cmake_prefix_path = os.environ.get('CMAKE_PREFIX_PATH', None)
    if cmake_prefix_path is None:
        return None
    paths = cmake_prefix_path.split(os.pathsep)
    paths = filter(lambda x: x.split(os.path.sep)[-1] not in packages, paths)
    return os.pathsep.join(paths)


def get_cmake_prefix_path_without_workspace(workspace_root):
    cmake_prefix_path = os.environ.get('CMAKE_PREFIX_PATH', None)
    if cmake_prefix_path is None:
        return None
    paths = cmake_prefix_path.split(os.pathsep)
    paths = filter(lambda x: not x.startswith(workspace_root), paths)
    return os.pathsep.join(paths)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    packages_arg = parser.add_argument('packages', nargs='*', help='If specified only these packages are built.')
    parser.add_argument('--logs', default=False, action='store_true')
    parser.add_argument('--force', default=False, action='store_true')

    args = parser.parse_args()
    workspace_root = get_workspace_root()
    packages = args.packages or get_packages_in_workspace()
    ament_prefix_path = get_ament_prefix_path_without_packages(packages)
    if ament_prefix_path is not None:
        print(f'export AMENT_PREFIX_PATH={ament_prefix_path};')
    cmake_prefix_path = get_cmake_prefix_path_without_packages(packages)
    if cmake_prefix_path is not None:
        print(f'export CMAKE_PREFIX_PATH={cmake_prefix_path};')

#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
from build import build_packages
from _clean import clean_packages
from helpers.output import error
from helpers.workspace import get_workspace_root, PackageChoicesCompleter
from helpers.remove_packages_from_env import *
import argcomplete
import argparse
import os

if __name__ == '__main__':
    workspace_root = get_workspace_root()
    parser = argparse.ArgumentParser()
    packages_arg = parser.add_argument('packages', nargs='*', help='If specified only these packages are built.')
    packages_arg.completer = PackageChoicesCompleter(workspace_root)
    parser.add_argument('--this', default=False, action='store_true')
    parser.add_argument('--force', default=False, action='store_true')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    packages = args.packages or []

    if workspace_root is None:
        error('You are not in a workspace!')
        exit(1)
    clean_packages(workspace_root, packages, force=args.force)
    ament_prefix_path = get_ament_prefix_path_without_packages(packages) if any(packages) \
        else get_ament_prefix_path_without_workspace(workspace_root)
    cmake_prefix_path = get_cmake_prefix_path_without_packages(packages) if any(packages) \
        else get_cmake_prefix_path_without_workspace(workspace_root)
    if ament_prefix_path is not None:
        os.environ['AMENT_PREFIX_PATH'] = ament_prefix_path
    if cmake_prefix_path is not None:
        os.environ['CMAKE_PREFIX_PATH'] = cmake_prefix_path
    exit(build_packages(workspace_root, packages))

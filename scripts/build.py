#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
from helpers.output import error
from helpers.workspace import get_workspace_root, PackageChoicesCompleter
import argcomplete
import argparse
import os
import subprocess
import sys


def build_packages(workspace_root, packages, env=None):
    os.chdir(workspace_root)
    if any(packages):
        command = subprocess.run(f'colcon build --packages-select {" ".join(packages)}',
                                 stdout=sys.stdout, stderr=sys.stderr, shell=True, env=env)
    else:
        command = subprocess.run('colcon build', stdout=sys.stdout, stderr=sys.stderr, shell=True, env=env)
    return command.returncode


if __name__ == '__main__':
    workspace_root = get_workspace_root()
    parser = argparse.ArgumentParser()
    packages_arg = parser.add_argument('packages', nargs='*', help='If specified only these packages are built.')
    packages_arg.completer = PackageChoicesCompleter(workspace_root)
    parser.add_argument('--this', default=False, action='store_true')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if workspace_root is None:
        error('You are not in a workspace!')
        exit()

    sys.exit(build_packages(workspace_root, args.packages or []))

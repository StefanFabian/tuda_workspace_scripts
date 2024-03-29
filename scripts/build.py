#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
from helpers.output import print_error
from helpers.workspace import get_workspace_root, PackageChoicesCompleter
import argcomplete
import argparse
from colcon_core import __version__ as colcon_core_version
from packaging import version
import os
import subprocess
import sys


def build_packages(workspace_root, packages, env=None, debug=False, no_deps=False, continue_on_error=False):
    os.chdir(workspace_root)
    arguments = []
    if debug:
        arguments += ['--cmake-args', '-DCMAKE_BUILD_TYPE=Debug']
    if continue_on_error:
        arguments += ['--continue-on-error']
    if any(packages):
        arguments += ['--packages-up-to'] if not no_deps else ['--packages-select']
        arguments += packages
    command = subprocess.run(f'colcon build {" ".join(arguments)}',
                             stdout=sys.stdout, stderr=sys.stderr, shell=True, env=env)
    return command.returncode


if __name__ == '__main__':
    workspace_root = get_workspace_root()
    parser = argparse.ArgumentParser()
    packages_arg = parser.add_argument('packages', nargs='*', help='If specified only these packages are built.')
    packages_arg.completer = PackageChoicesCompleter(workspace_root)
    parser.add_argument('--this', default=False, action='store_true')
    parser.add_argument('--debug', default=False, action='store_true')
    parser.add_argument('--no-deps', default=False, action='store_true')
    parser.add_argument('--continue-on-error', default=False, action='store_true')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if workspace_root is None:
        print_error('You are not in a workspace!')
        exit()

    sys.exit(build_packages(workspace_root, args.packages or [], debug=args.debug, no_deps=args.no_deps,
                            continue_on_error=args.continue_on_error))

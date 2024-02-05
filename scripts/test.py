#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
from tuda_workspace_scripts.print import print_error, print_info
from tuda_workspace_scripts.workspace import get_workspace_root, PackageChoicesCompleter
import argcomplete
import argparse
import os
import subprocess
import sys

if __name__ == '__main__':
    workspace_root = get_workspace_root()
    parser = argparse.ArgumentParser()
    packages_arg = parser.add_argument('packages', nargs='*', help='If specified only these packages are built.')
    packages_arg.completer = PackageChoicesCompleter(workspace_root)
    parser.add_argument('--this', default=False, action='store_true')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if workspace_root is None:
        print_error('You are not in a workspace!')
        exit()
    os.chdir(workspace_root)
    print_info('>>> Building packages')
    if args.packages is not None and len(args.packages) > 0:
        command = subprocess.run('colcon build --packages-select ' + ' '.join(args.packages),
                                 stdout=sys.stdout, stderr=sys.stderr, shell=True)
        if command.returncode != 0:
            print_error('>>> Failed to build packages')
            exit(command.returncode)
        print_info('>>> Running tests')
        command = subprocess.run('colcon test --packages-select ' + ' '.join(args.packages),
                                 stdout=sys.stdout, stderr=sys.stderr, shell=True)
        returncode = command.returncode
        for package in args.packages:
            print_info(f'>>> {package}')
            command = subprocess.run(f'colcon test-result --verbose --test-result-base build/{package}',
                                     stdout=sys.stdout, stderr=sys.stderr, shell=True)
            returncode |= command.returncode
    else:
        command = subprocess.run('colcon build', stdout=sys.stdout, stderr=sys.stderr, shell=True)
        if command.returncode != 0:
            print_error('>>> Failed to build packages')
            exit(command.returncode)
        print_info('>>> Running tests')
        command = subprocess.run('colcon test', stdout=sys.stdout, stderr=sys.stderr, shell=True)
        returncode = command.returncode
        command = subprocess.run('colcon test-result --verbose', stdout=sys.stdout, stderr=sys.stderr, shell=True)
        returncode |= command.returncode
    sys.exit(returncode)

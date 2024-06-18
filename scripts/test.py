#!/usr/bin/env python3
from tuda_workspace_scripts.build import build_packages
from tuda_workspace_scripts.print import print_error, print_info
from tuda_workspace_scripts.workspace import find_packages_in_directory, get_workspace_root, PackageChoicesCompleter
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
    parser.add_argument('--this', default=False, action='store_true', help='Test the packages in the current directory.')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if workspace_root is None:
        print_error('You are not in a workspace!')
        exit()

    packages = args.packages or []
    if args.this:
        packages = find_packages_in_directory(os.getcwd())
        if len(packages) == 0:
            print_error("No package found in the current directory!")
            exit(1)

    os.chdir(workspace_root)
    print_info('>>> Building packages')
    if len(packages) > 0:
        returncode = build_packages(workspace_root, packages)
        if returncode != 0:
            print_error('>>> Failed to build packages')
            exit(returncode)
        print_info('>>> Running tests')
        command = subprocess.run('colcon test --packages-select ' + ' '.join(packages),
                                 stdout=sys.stdout, stderr=sys.stderr, shell=True)
        returncode = command.returncode
        for package in packages:
            print_info(f'>>> {package}')
            command = subprocess.run(f'colcon test-result --verbose --test-result-base build/{package}',
                                     stdout=sys.stdout, stderr=sys.stderr, shell=True)
            returncode |= command.returncode
    else:
        returncode = build_packages(workspace_root)
        if returncode != 0:
            print_error('>>> Failed to build packages')
            exit(returncode)
        print_info('>>> Running tests')
        command = subprocess.run('colcon test', stdout=sys.stdout, stderr=sys.stderr, shell=True)
        returncode = command.returncode
        command = subprocess.run('colcon test-result --verbose', stdout=sys.stdout, stderr=sys.stderr, shell=True)
        returncode |= command.returncode
    sys.exit(returncode)

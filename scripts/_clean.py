#!/usr/bin/env python
from tuda_workspace_scripts.print import confirm, print_error, print_info
from tuda_workspace_scripts.workspace import get_workspace_root, PackageChoicesCompleter
from helpers.remove_packages_from_env import *
import argcomplete
import argparse
import os
import shutil


def clean_logs(workspace_root, packages=None, force=False):
    original_path = os.getcwd()
    os.chdir(workspace_root)
    if packages is not None and any(packages):
        print_error('--logs and packages are not compatible!')
        os.chdir(original_path)
        return 1
    print('  {}/log'.format(os.getcwd()))
    if force or confirm('Continue?'):
        shutil.rmtree('log', ignore_errors=True)
    else:
        print_info('Not deleted.')

    os.chdir(original_path)


def clean_packages(workspace_root, packages, force=False) -> bool:
    original_path = os.getcwd()
    os.chdir(workspace_root)
    try:
        print('I will delete:')
        if any(packages):
            if len(packages) <= 3:
                for package in packages:
                    print(f'  {os.getcwd()}/build/{package}')
                    print(f'  {os.getcwd()}/install/{package}')
            else:
                print(f'  {os.getcwd()}/build/[PACKAGES]')
                print(f'  {os.getcwd()}/install/[PACKAGES]')
        else:
            print(f'  {os.getcwd()}/build')
            print(f'  {os.getcwd()}/install')
            print(f'  {os.getcwd()}/log')

        if not force and not confirm('Continue?'):
            print_info('Not deleted.')
            return False
        
        if any(packages):
            for package in packages:
                shutil.rmtree(f'build/{package}', ignore_errors=True)
                shutil.rmtree(f'install/{package}', ignore_errors=True)
            ament_prefix_path = get_ament_prefix_path_without_packages(packages)
            cmake_prefix_path = get_cmake_prefix_path_without_packages(packages)
            print_info(f'>>> {len(packages)} package cleaned.')
        else:
            shutil.rmtree('build', ignore_errors=True)
            shutil.rmtree('install', ignore_errors=True)
            shutil.rmtree('log', ignore_errors=True)
            ament_prefix_path = get_ament_prefix_path_without_workspace(workspace_root)
            cmake_prefix_path = get_cmake_prefix_path_without_workspace(workspace_root)
            print_info(f'>>> All packages cleaned.')

        if ament_prefix_path is not None:
            os.environ['AMENT_PREFIX_PATH'] = ament_prefix_path
        if cmake_prefix_path is not None:
            os.environ['CMAKE_PREFIX_PATH'] = cmake_prefix_path
        print()
        return True
    finally:
        os.chdir(original_path)


if __name__ == '__main__':
    workspace_root = get_workspace_root()
    parser = argparse.ArgumentParser()
    packages_arg = parser.add_argument('packages', nargs='*', help='If specified only these packages are built.')
    packages_arg.completer = PackageChoicesCompleter(workspace_root)
    parser.add_argument('--force', default=False, action='store_true')
    parser.add_argument('--logs', default=False, action='store_true')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if workspace_root is None:
        print_error('You are not in a workspace!')
        exit()

    if args.logs:
        exit(clean_logs(workspace_root, args.packages or [], force=args.force))
    else:
        exit(clean_packages(workspace_root, args.packages or [], force=args.force))

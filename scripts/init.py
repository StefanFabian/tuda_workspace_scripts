#!/usr/bin/env python3
import argparse
import os
from tuda_workspace_scripts.print import *
from tuda_workspace_scripts.workspace import get_workspace_root

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--yes', '-y', action='store_true', help='Automatically answer yes to all questions.')
    parser.add_argument('--force', '-f', action='store_true', help='Force the command to run through in case of warnings. Used with -y.')
    args = parser.parse_args()

    try:
        alias = os.environ.get('TUDA_WSS_PREFIX', 'tuda_wss')
        if '.ros2_workspace' in os.listdir():
            print_error('This folder is already a workspace root.')
            exit(0)
        print('I will mark the current directory {} as a workspace root.'.format(os.getcwd()))
        print('This means the current directory will be used when building packages in this workspace using {}.'.format(alias))
        if 'src' not in os.listdir():
            print_warn('This directory does not contain a src folder. Are you sure it is a workspace root?')
            if args.yes and not args.force:
                print_warn('Use -f to force the command to run through.')
                exit(1)

        if get_workspace_root(os.getcwd()) is not None:
            print_warn('This folder is already in a ROS 2 workspace. Are you sure you want to continue?')
            if args.yes and not args.force:
                print_warn('Use -f to force the command to run through.')
                exit(1)

        if args.yes or confirm('Continue?'):
            # Create marker file
            with open('.ros2_workspace', 'w') as f:
                pass
        exit(0)
    except KeyboardInterrupt:
        exit(1)

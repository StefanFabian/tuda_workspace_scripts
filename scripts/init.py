#!/usr/bin/env python
import os
from helpers.output import *
from helpers.workspace import get_workspace_root

if __name__ == '__main__':
    alias = os.environ.get('TUDA_WSS_PREFIX', 'tuda_wss')
    if '.ros2_workspace' in os.listdir():
        print_error('This folder is already a workspace root.')
        exit()
    print('I will mark the current directory {} as a workspace root.'.format(os.getcwd()))
    print('This means the current directory will be used when building packages in this workspace using {}.'.format(alias))
    if 'src' not in os.listdir():
        print_warn('This directory does not contain a src folder. Are you sure it is a workspace root?')

    if get_workspace_root(os.getcwd()) is not None:
        print_warn('This folder is already in a ROS 2 workspace. Are you sure you want to continue?')

    if confirm('Continue?'):
        # Create marker file
        with open('.ros2_workspace', 'w') as f:
            pass

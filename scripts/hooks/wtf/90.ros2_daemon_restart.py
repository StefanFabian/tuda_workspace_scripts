#!/usr/bin/env python3
from tuda_workspace_scripts.print import print_header, print_info
import os


def fix():
    print_header("Restarting ROS2 daemon")
    os.system("ros2 daemon stop")
    os.system("ros2 daemon start")
    print_info("ROS2 daemon restarted")
    return False  # This should never end the fix chain

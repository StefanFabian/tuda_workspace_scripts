#!/usr/bin/env python3
from ament_index_python.packages import get_package_share_path
import argparse
import os
from pathlib import Path
import shutil
from tuda_workspace_scripts.print import *
from tuda_workspace_scripts.workspace import get_workspace_root


def mark_workspace(path: str | Path):
    """
    Mark a directory as a workspace root.
    This method can also be used on an existing workspace root without issue.
    """
    # Create marker and config directory .tuda_workspace_scripts
    os.makedirs(os.path.join(path, ".tuda_workspace_scripts"), exist_ok=True)
    # Create marker file .ros2_workspace
    Path(os.path.join(path, ".ros2_workspace")).touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Automatically answer yes to all questions.",
    )
    args = parser.parse_args()

    try:
        alias = os.environ.get("TUDA_WSS_PREFIX", "tuda_wss")
        # Check that current directory is not in a workspace
        workspace_root = get_workspace_root(os.getcwd())
        if workspace_root is not None:
            if workspace_root == os.getcwd():
                print_info("This folder is already marked as a workspace root.")
                print_info("Recreating missing markers if necessary.")
                mark_workspace(os.getcwd())
                exit(0)
            print_error(
                "This folder is already in a ROS 2 workspace! This is not supported."
            )
            exit(1)
        # Check that current directory does not contain a workspace
        for root, dirs, files in os.walk("."):
            if ".tuda_workspace_scripts" in dirs or ".ros2_workspace" in files:
                print_error(f"This folder contains a workspace root at {root}.")
                exit(1)

        print(f"I will mark the current directory {os.getcwd()} as a workspace root.")
        print(
            f"This means the current directory will be used when building packages in this workspace using {alias}."
        )
        if "src" not in os.listdir():
            print_warn("This directory does not contain a src folder.")

        if args.yes or confirm("Continue?"):
            mark_workspace(os.getcwd())
            print_info("Workspace root marked.")

        exit(0)
    except KeyboardInterrupt:
        print_error("Canceled by user.")
        exit(1)

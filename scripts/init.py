#!/usr/bin/env python3
from ament_index_python.packages import get_package_share_path
import argparse
import os
from pathlib import Path
import shutil
from tuda_workspace_scripts.print import *
from tuda_workspace_scripts.workspace import get_workspace_root

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Automatically answer yes to all questions."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the configuration files in the workspace root.",
    )
    args = parser.parse_args()

    try:
        alias = os.environ.get("TUDA_WSS_PREFIX", "tuda_wss")
        print_info(
            "Verifying that we are not in a workspace or a path containing a workspace."
        )
        if not args.reset:
            # Check that current directory is not in a workspace
            if get_workspace_root(os.getcwd()) is not None:
                print_error(
                    "This folder is already in a ROS 2 workspace! This is not supported."
                )
                exit(1)
            # Check that current directory does not contain a workspace
            for root, dirs, files in os.walk("."):
                if ".tuda_workspace_scripts" in dirs or ".ros2_workspace" in files:
                    print_error(f"This folder contains a workspace root at {root}.")
                    exit(1)
        elif get_workspace_root(os.getcwd()) not in [os.getcwd(), None]:
            print_error("Reset can only be used in a workspace root directory.")
            exit(1)

        print(f"I will mark the current directory {os.getcwd()} as a workspace root.")
        print(
            f"This means the current directory will be used when building packages in this workspace using {alias}."
        )
        if "src" not in os.listdir():
            print_warn("This directory does not contain a src folder.")

        if args.yes or confirm("Continue?"):
            # Create marker and config directory .tuda_workspace_scripts
            os.makedirs(".tuda_workspace_scripts/colcon_config", exist_ok=True)
            print_info("Workspace root marked.")
            # Copy files from templates directory
            templates_path = (
                get_package_share_path("tuda_workspace_scripts") / "templates"
            )
            colcon_config_path = Path(".tuda_workspace_scripts/colcon_config")
            if args.reset or not os.path.exists(colcon_config_path / "defaults.yaml"):
                shutil.copyfile(
                    templates_path / "colcon_defaults.yaml",
                    colcon_config_path / "defaults.yaml",
                )
                print_info("Copied default colcon config.")

        exit(0)
    except KeyboardInterrupt:
        print_error("Canceled by user.")
        exit(1)

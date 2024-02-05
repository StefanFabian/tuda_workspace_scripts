#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
from tuda_workspace_scripts import load_config
from tuda_workspace_scripts.print import print_error
from tuda_workspace_scripts.workspace import get_workspace_root, PackageChoicesCompleter
import argcomplete
import argparse

try:
    import colcon_override_check
except ImportError:
    colcon_override_check = None
import os
import subprocess
import sys


def build_packages(
    packages,
    env=None,
    build_type=None,
    no_deps=False,
    continue_on_error=False,
) -> int:
    workspace_root = get_workspace_root()
    if workspace_root is None:
        print_error("You are not in a workspace!")
        return 1
    os.chdir(workspace_root)
    config = load_config()
    arguments = []
    if build_type is not None:
        arguments += ["--cmake-args", f"-DCMAKE_BUILD_TYPE={build_type}"]
    if colcon_override_check is not None and any(packages):
        arguments += ["--allow-overriding"] + packages
    if continue_on_error:
        arguments += ["--continue-on-error"]
    if config.variables.workspace_install == 'symlink':
        arguments += ["--symlink-install"]
    elif config.variables.workspace_install == 'merge':
        arguments += ["--merge-install"]
    if any(packages):
        arguments += ["--packages-up-to"] if not no_deps else ["--packages-select"]
        arguments += packages
    command = subprocess.run(
        f'colcon build {" ".join(arguments)}',
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=True,
        env=env,
    )
    return command.returncode


if __name__ == "__main__":
    workspace_root = get_workspace_root()
    parser = argparse.ArgumentParser()
    packages_arg = parser.add_argument(
        "packages", nargs="*", help="If specified only these packages are built."
    )
    packages_arg.completer = PackageChoicesCompleter(workspace_root)
    parser.add_argument("--this", default=False, action="store_true")
    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--rel-with-deb-info", default=False, action="store_true")
    parser.add_argument("--no-deps", default=False, action="store_true")
    parser.add_argument("--continue-on-error", default=False, action="store_true")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if workspace_root is None:
        print_error("You are not in a workspace!")
        exit()

    build_type = None
    if args.debug:
        build_type = "Debug"
    elif args.rel_with_deb_info:
        build_type = "RelWithDebInfo"

    sys.exit(
        build_packages(
            args.packages or [],
            build_type=build_type,
            no_deps=args.no_deps,
            continue_on_error=args.continue_on_error,
        )
    )

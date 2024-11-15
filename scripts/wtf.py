#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
from tuda_workspace_scripts.print import *
from tuda_workspace_scripts.scripts import get_hooks_for_command
from tuda_workspace_scripts.workspace import get_workspace_root
import importlib.util


def load_method_from_file(file_path: str, method_name: str):
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, method_name)


def main():
    parser = argparse.ArgumentParser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if get_workspace_root() is None:
        print_workspace_error()
        return 1

    count_fixes = 0
    hooks = list(sorted(get_hooks_for_command("wtf")))
    # Collect all wtf scripts in hooks/wtf folders of TUDA_WSS_SCRIPTS environment variable
    for script in hooks:
        # Load script and run fix command and obtain result
        fix = load_method_from_file(script, "fix")
        if fix():
            count_fixes += 1
    if count_fixes > 0:
        print_success(f"{len(hooks)} checks have fixed {count_fixes} potential issues.")
    else:
        print_success(f"{len(hooks)} checks have found no potential issues.")


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print_warn("Stopping per user request.")
        print("Good bye.")
        exit(0)

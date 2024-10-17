#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
from tuda_workspace_scripts.print import print_error, print_info, confirm
from tuda_workspace_scripts.scripts import get_hooks_for_command
import importlib.util


def load_method_from_file(file_path: str, method_name: str):
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, method_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--continue-on-fix",
        default=False,
        action="store_true",
        help="Continue running fixes even if one fix was successful.",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    continue_on_fix = args.continue_on_fix
    fixed_something = False
    # Collect all wtf scripts in hooks/wtf folders of TUDA_WSS_SCRIPTS environment variable
    for script in sorted(get_hooks_for_command("wtf")):
        if fixed_something and not continue_on_fix:
            if confirm(f"This might have fixed your issue! Continue anyway?"):
                break
            continue_on_fix = True
        # Load script and run fix command and obtain result
        fix = load_method_from_file(script, "fix")
        if fix():
            fixed_something = True

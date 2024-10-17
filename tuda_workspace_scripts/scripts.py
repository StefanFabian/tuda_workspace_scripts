import os
from typing import Generator


def get_scripts_dirs() -> list[str]:
    return os.environ.get("TUDA_WSS_SCRIPTS", "").split(os.pathsep)

def get_hook_dirs() -> Generator[str, None, None]:
    for script_dir in get_scripts_dirs():
        hook_dir = os.path.join(script_dir, "hooks")
        if os.path.isdir(hook_dir):
            yield hook_dir

def get_hooks_for_command(command: str) -> Generator[str, None, None]:
    for hook_dir in get_hook_dirs():
        command_hook = os.path.join(hook_dir, command)
        if os.path.isdir(command_hook):
            for script in os.listdir(command_hook):
                script_path = os.path.join(command_hook, script)
                if os.path.isfile(script_path):
                    yield script_path

from .workspace import get_workspace_root
import os
import shutil
from typing import Any, Generator
import yaml

# Use the environment variable TUDA_WSS_CONFIG to specify a config file or directory.
# You can also specify multiple files and directories separated by the os path separator.
# If not specified, default to WORKSPACE_ROOT/.config/tuda_workspace_scripts.yaml
ROBOTS_CONFIG_FILE_PATH = os.getenv("TUDA_WSS_ROBOTS", None)
if ROBOTS_CONFIG_FILE_PATH is None:
    ROBOTS_CONFIG_FILE_PATH = get_workspace_root()
    if ROBOTS_CONFIG_FILE_PATH is not None:
        ROBOTS_CONFIG_FILE_PATH += "/.config/robots.yaml"


__CACHE = {}


class Command:
    def __init__(self, name: str, command: str):
        self.name = name
        self.command = command

    def get_command(self) -> str:
        return self.command


class RemotePC:
    def __init__(self, name: str, hostname: str, user: str, commands: list[Command]):
        self.name = name
        self.hostname = hostname
        self.user = user
        self.commands = commands

    def has_command(self, name: str) -> bool:
        for cmd in self.commands:
            if cmd.name == name:
                return True
        return

    def get_command(self, command_name: str) -> str:
        """
        Get the shell command to execute the given command on this remote PC.
        @raises ValueError if the command is not found.
        """
        for cmd in self.commands:
            if cmd.name == command_name:
                if command_name == "ssh-copy-id":
                    return f"ssh-copy-id {self.user}@{self.hostname}"
                return f"ssh -t {self.user}@{self.hostname} '{cmd.get_command().replace("'", "\\'")}'"
        raise ValueError(f"Command {command_name} not found in remote PC {self.name}")


class Robot:
    def __init__(self, name: str, remote_pcs: dict[str, RemotePC]):
        self.name = name
        self.remote_pcs = remote_pcs

    def get_commands(self, command_name: str) -> Generator[tuple[str, str], None, None]:
        """
        Get the shell commands to execute the given command on all remote PCs that support it.
        @raises ValueError if the command is not found in any remote PC.
        """
        if not any([pc.has_command(command_name) for pc in self.remote_pcs.values()]):
            raise ValueError(f"Command {command_name} not found in any remote PC")
        for pc in self.remote_pcs.values():
            if pc.has_command(command_name):
                yield (pc.name, pc.get_command(command_name))


DEFAULT_COMMANDS = [
    Command("ssh", ""),
    Command("ssh-copy-id", ""),
    Command("reboot", "sudo reboot now"),
    Command("shutdown", "sudo shutdown now"),
]


def _load_robot_from_yaml(name, config: dict[str, Any]) -> Robot:
    remote_pcs = dict()
    shared_commands = dict([(cmd.name, cmd) for cmd in DEFAULT_COMMANDS])
    if "commands" in config:
        for command_name in config["commands"]:
            # Default commands can be disabled by setting them to None.
            if config["commands"][command_name] is None:
                del shared_commands[command_name]
                continue
            shared_commands[command_name] = Command(command_name, config["commands"][command_name])
    for pc_name in config["remote_pcs"]:
        pc_config = config["remote_pcs"][pc_name]
        if "user" not in pc_config:
            raise ValueError(f"User not specified for remote PC {pc_name}")
        user = pc_config["user"]
        hostname = pc_config["hostname"] if "hostname" in pc_config else pc_name
        commands = dict(shared_commands)
        if "commands" in pc_config:
            for command_name in pc_config["commands"]:
                if pc_config["commands"][command_name] is None:
                    del commands[command_name]
                    continue
                commands[command_name] = Command(command_name, pc_config["commands"][command_name])
        remote_pcs[pc_name] = RemotePC(pc_name, hostname, user, list(commands.values()))
    return Robot(config["name"] if "name" in config else name, remote_pcs)


def _load_robot_config_from_file(path: str) -> dict[str, Robot]:
    if path in __CACHE:
        return __CACHE[path]
    robots = {}
    with open(path, "r") as f:
        config = yaml.safe_load(f)
        if "remote_pcs" in config:
            # It's a robot
            filename = os.path.basename(path)
            name = os.path.splitext(filename)[0]
            return {name: _load_robot_from_yaml(name, config)}
        # It's multiple robots
        for name in config:
            robots[name] = _load_robot_from_yaml(name, config[name])
    __CACHE[path] = robots
    return robots


def _load_robots_from_dir(path: str) -> dict[str, Robot]:
    if path in __CACHE:
        return __CACHE[path]
    robots: dict = {}
    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith(".yaml"):
                continue
            robots.update(_load_robot_config_from_file(os.path.join(root, file)))
    __CACHE[path] = robots
    return robots


def load_robots() -> dict[str, Robot]:
    robots = {}
    # Split the config file path by the os path separator
    for path in ROBOTS_CONFIG_FILE_PATH.split(os.pathsep):
        if not os.path.exists(path):
            continue
        if os.path.isdir(path):
            robots.update(_load_robots_from_dir(path))
        else:
            robots.update(_load_robot_config_from_file(path))
    return robots


def get_robot(name: str) -> Robot:
    """
    Get a robot by name
    @raises ValueError if the robot does not exist
    """
    robots = load_robots()
    if name not in robots:
        raise ValueError(f"Robot {name} not found")
    return robots[name]

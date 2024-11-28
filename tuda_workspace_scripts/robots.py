from .workspace import get_workspace_root
import os
from jinja2 import Template
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


class RenderedCommand:
    def __init__(self, command: str, delegate_to: str | None):
        self.command = command
        self.delegate_to = delegate_to


class Command:
    def __init__(self, name: str, command: str, delegate_to: str | None = None):
        self.name = name
        self.command = command
        self.delegate_to = delegate_to

    def render_command(self, vars: dict) -> RenderedCommand:
        return RenderedCommand(Template(self.command).render(vars), self.delegate_to)


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
        return False

    def render_command(self, command_name: str, vars: dict = {}) -> RenderedCommand:
        """
        Get the shell command to execute the given command on this remote PC.
        @raises ValueError if the command is not found.
        """
        base_vars = {"hostname": self.hostname, "user": self.user}
        base_vars.update(vars)
        for cmd in self.commands:
            if cmd.name == command_name:
                return cmd.render_command(base_vars)

        raise ValueError(f"Command {command_name} not found in remote PC {self.name}")


class Robot:
    def __init__(self, name: str, remote_pcs: dict[str, RemotePC]):
        self.name = name
        self.remote_pcs = remote_pcs

    def _get_shell_command(self, pc: RemotePC, command: RenderedCommand) -> RemotePC:
        if command.delegate_to == "localhost" or command.delegate_to == "127.0.0.1":
            return command.command
        target = pc
        if command.delegate_to is not None:
            if command.delegate_to not in self.remote_pcs:
                raise ValueError(
                    f"Remote PC {command.delegate_to} not found in robot {self.name}"
                )
            target = self.remote_pcs[command.delegate_to]
        return f"ssh -t {target.user}@{target.hostname} '{command.command.replace("'", "\\'")}'"

    def render_commands(
        self, command_name: str, vars: dict = {}
    ) -> Generator[tuple[str, str], None, None]:
        """
        Get the shell commands to execute the given command on all remote PCs that support it.
        @raises ValueError if the command is not found in any remote PC.
        """
        if not any([pc.has_command(command_name) for pc in self.remote_pcs.values()]):
            raise ValueError(f"Command {command_name} not found in any remote PC")
        base_vars = {"robot": self.name}
        base_vars.update(vars)
        for pc in self.remote_pcs.values():
            if pc.has_command(command_name):
                rendered_command = pc.render_command(command_name, base_vars)
                shell_command = self._get_shell_command(pc, rendered_command)
                yield (pc.name, shell_command)


DEFAULT_COMMANDS = [
    Command("ssh", "ssh {{user}}@{{hostname}}", delegate_to="localhost"),
    Command(
        "ssh-copy-id", "ssh-copy-id {{user}}@{{hostname}}", delegate_to="localhost"
    ),
    Command("reboot", "sudo reboot now"),
    Command("shutdown", "sudo shutdown now"),
]


def _load_command_from_yaml(name: str, config: dict[str, Any] | str) -> Command:
    if isinstance(config, str):
        return Command(name, config)
    delegate_to = None
    if "delegate_to" in config:
        delegate_to = config["delegate_to"]
    return Command(name, config["command"], delegate_to)


def _load_pc_from_yaml(
    pc_name: str, config: dict[str, Any], shared_commands: dict
) -> RemotePC:
    if "user" not in config:
        raise ValueError(f"User not specified for remote PC {pc_name}")
    user = config["user"]
    hostname = config["hostname"] if "hostname" in config else pc_name
    commands = dict(shared_commands)
    if "commands" in config:
        for name in config["commands"]:
            if config["commands"][name] is None:
                del commands[name]
                continue
            commands[name] = _load_command_from_yaml(name, config["commands"][name])
    return RemotePC(pc_name, hostname, user, list(commands.values()))


def _load_robot_from_yaml(name, config: dict[str, Any]) -> Robot:
    remote_pcs = dict()
    shared_commands = dict([(cmd.name, cmd) for cmd in DEFAULT_COMMANDS])
    if "commands" in config:
        for command_name in config["commands"]:
            # Default commands can be disabled by setting them to None.
            if config["commands"][command_name] is None:
                del shared_commands[command_name]
                continue
            shared_commands[command_name] = Command(
                command_name, config["commands"][command_name]
            )
    for pc_name in config["remote_pcs"]:
        pc_config = config["remote_pcs"][pc_name]
        remote_pcs[pc_name] = _load_pc_from_yaml(pc_name, pc_config, shared_commands)
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

#!/usr/bin/env python3
from psutil import process_iter
from tuda_workspace_scripts.print import confirm, print_header, print_info, print_error


def fix() -> bool:
    print_header("Checking for zombies")
    gz_processes = []
    for p in process_iter(["pid", "name", "cmdline"]):
        if p.info["name"] == "ruby" and p.info["cmdline"][0].startswith("gz sim"):
            gz_processes.append(p)
    if len(gz_processes) == 0:
        print_info("No zombies found.")
        return False
    has_server = any(["-s" in p.info["cmdline"][0] for p in gz_processes])
    has_gui = any(["-g" in p.info["cmdline"][0] for p in gz_processes])
    if has_server and has_gui:
        print_info("Found gazebo server and gui. Assuming they are not zombies.")
        return False
    print_error("Found gazebo zombies.")
    if not confirm("Kill them?"):
        return False
    for p in gz_processes:
        p.kill()
    print_info("Killed all zombies.")
    return True


if __name__ == "__main__":
    fix()

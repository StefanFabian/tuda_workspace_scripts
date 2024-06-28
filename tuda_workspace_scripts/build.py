from .config import load_config
from .print import confirm, print_error, print_info
from .workspace import *
import os
import shlex
import shutil
import subprocess
import sys

try:
    import colcon_override_check
except ImportError:
    colcon_override_check = None


def build_packages(
    workspace_root,
    packages=None,
    env=None,
    build_type=None,
    no_deps=False,
    continue_on_error=False,
    build_tests=False,
) -> int:
    os.chdir(workspace_root)
    arguments = []
    if colcon_override_check is not None and any(packages):
        arguments += ["--allow-overriding"] + packages
    if continue_on_error:
        arguments += ["--continue-on-error"]

    cmake_arguments = []
    if build_type is not None:
        cmake_arguments.append(f"-DCMAKE_BUILD_TYPE={build_type}")
    if build_tests:
        cmake_arguments.append("-DBUILD_TESTING=ON")
    if any(cmake_arguments):
        arguments += ["--cmake-args"] + list(map(lambda x: f"' {shlex.quote(x)}'", cmake_arguments))

    if any(packages):
        arguments += ["--packages-up-to"] if not no_deps else ["--packages-select"]
        arguments += packages
    
    print_info("Command:")
    print(f"colcon build {' '.join(arguments)}")
    print_info(f">>> Running in {workspace_root}")
    command = subprocess.run(
        f'colcon build {" ".join(arguments)}',
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=True,
        env=env,
    )
    return command.returncode


def clean_logs(workspace_root, packages=None, force=False):
    original_path = os.getcwd()
    os.chdir(workspace_root)
    if packages is not None and any(packages):
        print_error("--logs and packages are not compatible!")
        os.chdir(original_path)
        return 1
    print("  {}/log".format(os.getcwd()))
    if force or confirm("Continue?"):
        shutil.rmtree("log", ignore_errors=True)
    else:
        print_info("Not deleted.")

    os.chdir(original_path)


def clean_packages(workspace_root, packages, force=False) -> bool:
    original_path = os.getcwd()
    os.chdir(workspace_root)
    try:
        print("I will delete:")
        if any(packages):
            print(f'  {os.getcwd()}/build/{{{",".join(packages)}}}')
            print(f'  {os.getcwd()}/install/{{{",".join(packages)}}}')
        else:
            print(f"  {os.getcwd()}/build")
            print(f"  {os.getcwd()}/install")
            print(f"  {os.getcwd()}/log")

        if not force and not confirm("Continue?"):
            print_info("Not deleted.")
            return False

        if any(packages):
            for package in packages:
                shutil.rmtree(f"build/{package}", ignore_errors=True)
                shutil.rmtree(f"install/{package}", ignore_errors=True)
            ament_prefix_path = get_ament_prefix_path_without_packages(packages)
            cmake_prefix_path = get_cmake_prefix_path_without_packages(packages)
            print_info(f">>> {len(packages)} package cleaned.")
        else:
            shutil.rmtree("build", ignore_errors=True)
            shutil.rmtree("install", ignore_errors=True)
            shutil.rmtree("log", ignore_errors=True)
            ament_prefix_path = get_ament_prefix_path_without_workspace(workspace_root)
            cmake_prefix_path = get_cmake_prefix_path_without_workspace(workspace_root)
            print_info(f">>> All packages cleaned.")

        if ament_prefix_path is not None:
            os.environ["AMENT_PREFIX_PATH"] = ament_prefix_path
        if cmake_prefix_path is not None:
            os.environ["CMAKE_PREFIX_PATH"] = cmake_prefix_path
        print()
        return True
    finally:
        os.chdir(original_path)

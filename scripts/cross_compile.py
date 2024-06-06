#!/usr/bin/env python3
import argcomplete
import argparse
from datetime import datetime, timezone
from dateutil.parser import parse as parse_date
import docker
from shutil import copytree, rmtree
from tuda_workspace_scripts import StatusOutput, print_info, print_error
from tuda_workspace_scripts.workspace import PackageChoicesCompleter, get_workspace_root
from os import getenv, getuid, getgid
import os.path
import sys

# docker run --rm -it -v ~/workspaces/noetic/src:/workspace/src:ro -v /tmp/install:/workspace/install:rw --env ROS_DISTRO=noetic --platform arm64 cross-compile-arm64 workspace_scripts


def cross_compile(
    packages: str | list[str],
    ros_distro: str,
    platform: str,
    output_base_dir: str,
    output_dir: str | None = None,
    build_type: str = "RelWithDebInfo",
    clean: bool = False,
    no_cache: bool = False,
    rebuild: bool = False,
    pull: bool = False,
    base_image: str | None = None
) -> bool:
    # if packages is iterable, join them
    if isinstance(packages, list):
        packages = " ".join(packages)
    platform_cleaned = platform.replace(":", "_").replace("/", "_")
    if output_dir is None:
        output_dir = output_base_dir
        output_dir = os.path.join(output_dir, ros_distro, platform_cleaned)
    os.makedirs(output_dir, exist_ok=True)
    if base_image is None:
        tag = f"cross-compile-{ros_distro}-{platform_cleaned}"
        print_info(f">>> Obtain image for {ros_distro} on {platform}")
    else:
        base_image_cleaned = base_image.replace(":", "_").replace("/", "_")
        tag = f"cross-compile-{base_image_cleaned}-{platform_cleaned}"
        print_info(f">>> Obtain image based on {base_image} for {platform}")
    docker_client = docker.from_env()
    if not rebuild:
        try:
            image = docker_client.images.get(tag)
            created = (
                datetime.now(timezone.utc)
                if "Created" not in image.attrs
                else parse_date(image.attrs["Created"])
            )
            if (datetime.now(timezone.utc) - created).days > 14:
                print("Container might be outdated. Rebuilding without cache...")
                rebuild = True
                no_cache = True
        except docker.errors.ImageNotFound:
            rebuild = True
    if rebuild:
        path = os.path.join(
            getenv("TUDA_WSS_BASE", os.path.dirname(os.path.dirname(__file__))),
            "docker",
            "cross_compile",
        )
        if not os.path.isfile(os.path.join(path, "Dockerfile")):
            raise RuntimeError("Could not find Dockerfile in " + path)
        if base_image is not None:
            print_info(f">>> Pulling {base_image}")
            result = docker_client.api.pull(base_image, platform=platform, stream=True, decode=True)
            # Compute total progress from individual progress
            progress = {}
            current = 0
            total = 0
            ids = set()
            for item in result:
                if "id" in item:
                    ids.add(item["id"])
                if "progress" in item:
                    text = item["progress"].strip()
                    detail = item["progressDetail"]
                    if "current" in detail:
                        progress[item["id"]] = {"current": detail["current"], "total": detail["total"]}
                        current = sum([p["current"] for p in progress.values()]) / 1024 / 1024
                        total = sum([p["total"] for p in progress.values()]) / 1024 / 1024
                    print(f"{int(current / total * 100)}% ({int(current)}MB / {int(total)}MB) [{len(progress)}/{len(ids)} Layers]", end="\r")
                if "errorDetail" in item:
                    print("\033[K"+item["errorDetail"]["message"], file=sys.stderr)
                    return False
            print("\033[KDone.")
        print_info(">>> Building image")
        result = docker_client.api.build(
            decode=True,
            path=path,
            tag=tag,
            buildargs={
                "BASE_IMAGE": base_image,
                "ROS_DISTRO": ros_distro,
                "USER_ID": f"{getuid()}",
                "GROUP_ID": f"{getgid()}",
            },
            platform=platform,
            pull=pull,
            rm=True,
            forcerm=True,
            nocache=no_cache,
            use_config_proxy=True,
        )

        output = StatusOutput(12)
        full_log = ""
        for item in result:
            if "stream" in item:
                text = item["stream"].strip()
                if text:
                    full_log += text + "\n"
                    output.status(text)
            if "errorDetail" in item:
                output.clear()
                print(full_log)
                print_error(item["errorDetail"]["message"])
                return False
        output.clear()
        print(f"Done. Built image as {tag}")
    else:
        print(f"Using existing image {tag}")
    print_info(f">>> Cross-compiling {packages}")
    output = StatusOutput(10)
    container = None
    try:
        tmp_path = f"/tmp/tudawss/{tag}"
        if clean:
            def ignore_file_not_found(func, path, exc_info):
                if isinstance(exc_info[1], FileNotFoundError):
                    return
                func(path)

            rmtree(f"{tmp_path}/build", onerror=ignore_file_not_found)
            rmtree(f"{tmp_path}/devel", onerror=ignore_file_not_found)
            rmtree(f"{tmp_path}/install", onerror=ignore_file_not_found)
            rmtree(f"{tmp_path}/log", onerror=ignore_file_not_found)
        os.makedirs(f"{tmp_path}/build", exist_ok=True)
        os.makedirs(f"{tmp_path}/devel", exist_ok=True)
        os.makedirs(f"{tmp_path}/install", exist_ok=True)
        os.makedirs(f"{tmp_path}/log", exist_ok=True)
        container = docker_client.containers.run(
            tag,
            command=f"{packages}",
            volumes={
                os.path.join(get_workspace_root(), "src"): {
                    "bind": "/workspace/src",
                    "mode": "ro",
                },
                f"{tmp_path}/build": {
                    "bind": "/workspace/build",
                    "mode": "rw",
                },
                f"{tmp_path}/devel": {
                    "bind": "/workspace/devel",
                    "mode": "rw",
                },
                f"{tmp_path}/install": {
                    "bind": "/workspace/install",
                    "mode": "rw",
                },
                f"{tmp_path}/log": {
                    "bind": "/workspace/log",
                    "mode": "rw",
                },
                f"{tmp_path}/log": {
                    "bind": "/workspace/logs",
                    "mode": "rw",
                },
            },
            environment={"BUILD_TYPE": build_type},
            platform=platform,
            detach=True,
            stdout=True,
            stderr=True,
        )
        for line in container.logs(stream=True):
            text: str = line.decode("utf-8").strip()
            if ">>> Building workspace" in text:
                output.clear()
                output.disable_overwrite()
            if text:
                output.status(text)
        result = container.wait()
        if result["StatusCode"] != 0:
            print_error(
                f"Cross-compilation failed with exit code {result['StatusCode']}"
            )
            return False
        print_info(f">>> Copying results")
        # Copy install folder to workspace
        copytree(f"{tmp_path}/install", output_dir, dirs_exist_ok=True)
        print(f"Copied build results to {output_dir}")
    except docker.errors.ContainerError as e:
        print_error(f"Failed to cross-compile {packages}:")
        print(e.stderr.decode("utf-8"), file=sys.stderr)
        return False
    except KeyboardInterrupt:
        if container is not None:
            container.kill()
            print_info("Container killed.")
    finally:
        if container is not None:
            container.remove()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Builds the given packages for the given platform/architecture in a docker image.")
    parser.add_argument("--base-image", help="Use the given base image instead of the default one generated based on platform and distro.")
    parser.add_argument("--build-type", choices=["Debug", "RelWithDebInfo", "Release"])
    parser.add_argument(
        "--no-cache",
        default=False,
        action="store_true",
        help="Do not use the cache when building. Use with --rebuild for a clean build of the docker image.",
    )
    parser.add_argument("--pull", default=False, action="store_true", help="Pull base image before building.")
    parser.add_argument(
        "--rebuild",
        default=False,
        action="store_true",
        help="Force rebuilding the docker image.",
    )
    parser.add_argument(
        "--clean",
        default=False,
        action="store_true",
        help="Clean build folders before building.",
    )
    parser.add_argument(
        "--platform", choices=["linux/arm64", "linux/amd64"], required=True
    )
    parser.add_argument(
        "--ros-distro",
        choices=["foxy", "galactic", "humble", "iron"],
        default=getenv("ROS_DISTRO"),
        help="ROS distro to use for cross-compilation. Defaults to ROS distro on host.",
    )
    workspace_path = get_workspace_root()
    parser.add_argument(
        "--output-base-dir",
        default=os.path.join(workspace_path, "cross-compile-install"),
        help="Base directory where the install output is places. It will be placed in a subdirectory based on the ROS distro and platform.",
    )
    parser.add_argument("--output-dir", default=None, help="Use to specify an exact directory where the install output will be placed. Overwrites --output-base-dir.")
    package_arg = parser.add_argument(
        "PACKAGE", nargs="*", help="Packages to cross-compile"
    )
    package_arg.completer = PackageChoicesCompleter(get_workspace_root())
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not cross_compile(
        packages=args.PACKAGE,
        ros_distro=args.ros_distro,
        platform=args.platform,
        clean=args.clean,
        no_cache=args.no_cache,
        rebuild=args.rebuild,
        output_base_dir=args.output_base_dir,
        output_dir=args.output_dir,
        base_image=args.base_image,
        pull=args.pull,
    ):
        exit(1)

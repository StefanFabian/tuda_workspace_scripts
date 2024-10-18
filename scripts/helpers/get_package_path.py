#!/usr/bin/env python3
from tuda_workspace_scripts.workspace import get_package_path
import sys

if __name__ == "__main__":
    print(get_package_path(sys.argv[1]) or "")

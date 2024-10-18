#!/usr/bin/env python3
from tuda_workspace_scripts.workspace import get_packages_in_workspace

if __name__ == "__main__":
    print("\n".join(get_packages_in_workspace()))

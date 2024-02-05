# The TUDA Workspace Scripts

The TUDA workspace scripts add convenience scripts to manage a workspace and robots.

## Extending

### Add commands

You can add commands either in this repository in the scripts folder or as an overlay in a separate package.
Either way scripts have to be put in a scripts directory and three command forms are supported:

* Executable python files, e.g. command.py: The extension is stripped and the python file executed
* Executable bash/sh files, e.g. command.bash: The extension is stripped and the bash script is executed 
* Non-executable bash/sh files, e.g. command.bash: The file is sourced and may modify the environment

In each case the additional arguments are forwarded to the command.

### Overlay

To create an overlay, create a new package with a scripts folder, create an env-hook-in-file `setup.dsv.in` with the following content:

```dsv
prepend-non-duplicate;TUDA_WSS_SCRIPTS;share/@PROJECT_NAME@/scripts
```

In your `CMakeLists.txt` install the folder and file as follows:

```cmake
if (WIN32)
  message(FATAL_ERROR "Windows is currently not supported! Feel free to add support :)")
else()
  ament_environment_hooks(setup.dsv.in)
endif()

install(DIRECTORY docker scripts DESTINATION share/${PROJECT_NAME} USE_SOURCE_PERMISSIONS)
```

## Python Library

In your commands, you can use the `tuda_workspace_scripts` python module which contains a `print` and a `workspace` submodule.

### config

Provides a workspace configuration mechanism. You can use `load_config()` to obtain the current config.
Variables can be provided using a yaml file (see `config.yaml`), the files have to be registered using

```dsv
prepend-non-duplicate;TUDA_WSS_CONFIGS;share/@PROJECT_NAME@/config.yaml
```

The registered variables can be set using the `tuda_wss config` command.

### print

Provides helpers for printing.

* Colored output using `print_color`, `print_info`, `print_warn` and `print_error`
* Yes/No confirm questions on terminal with `confirm`
* Bounded logging: A limited number of status info lines are writen to the output. When line_count is reached old lines are overwritten.

### workspace

* Locate workspace director using `get_workspace_root`
* Find packages in a directory / in the workspace
  * also includes a `PackageChoicesCompleter` for `argcomplete`

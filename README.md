# The TUDA Workspace Scripts

The TUDA workspace scripts add convenience scripts to manage a workspace and robots. 

# Extending
## Add commands

You can add commands either in this repository in the scripts folder or as an overlay in a separate package.
Either way scripts have to be put in a scripts directory and three command forms are supported:

* Executable python files, e.g. command.py: The extension is stripped and the python file executed
* Executable bash/sh files, e.g. command.bash: The extension is stripped and the bash script is executed 
* Non-executable bash/sh files, e.g. command.bash: The file is sourced and may modify the environment

In each case the additional arguments are forwarded to the command.

## Overlay

To create an overlay, create a new package with a scripts folder and

import libtmux


def launch_tmux(
    commands: dict | list[str],
    session_name: str | None = None,
    use_windows: bool = False,
    keep_open_duration: int | None = 5,
):
    """
    Launch a tmux session and execute the given commands in panes or windows.
    @param commands: Commands to run in each pane or window.\
        If a dict is provided, the keys are used as names.
    @param session_name: Name of the tmux session. Defaults to None.
    @param use_windows: If True, each command is executed in a separate window;\
        if False, panes are used. Defaults to False.
    @param keep_open_duration: Time in seconds to keep each pane or window open after the\
        command completes. Defaults to 5. Set to None to keep open indefinitely.
    """
    command_names = list(commands.keys()) if isinstance(commands, dict) else commands
    shell_commands = commands if isinstance(commands, list) else list(commands.values())

    server = libtmux.Server()
    session = server.new_session(session_name=session_name)
    window = session.attached_window
    panes = [window.attached_pane]
    if use_windows:
        window.rename_window(command_names[0])
        for i in range(1, len(commands)):
            panes.append(session.new_window(window_name=command_names[i]).attached_pane)
    else:
        # Arrange panes in a tiled layout (grid)
        for i in range(1, len(shell_commands)):
            panes.append(window.split_window())
            window.select_layout("tiled")

    for i, command in enumerate(shell_commands):
        if keep_open_duration is not None:
            command = f"{command}; sleep {keep_open_duration}; exit"
        panes[i].window.select()
        panes[i].select()
        panes[i].send_keys(command)
    try:
        session.attach()
        session.kill()
    except:
        pass

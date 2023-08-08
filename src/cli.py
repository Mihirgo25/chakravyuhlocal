import click
import uvicorn
import socket
from IPython.core.ultratb import VerboseTB
import os
from configs.definitions import ROOT_DIR

EXEC_LINES = [
    "%load_ext autoreload",
    "%autoreload 2",
]

EXCLUDE_FILES = ["setup.py"]


def get_py_files(directory, excluded_dirs):
    py_files = []
    main_files = []
    for root, dirs, files in os.walk(directory):
        if any(excluded_dir in root for excluded_dir in excluded_dirs):
            continue

        for file in files:
            if file.endswith(".py") and file not in EXCLUDE_FILES:
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                    if (
                        "__name__ == '__main__'" in content
                        or '__name__ == "__main__"' in content
                    ):
                        main_files.append(relative_path)
                        continue
                py_files.append(relative_path)
    return py_files, main_files


dirs_to_ignore = [
    ".git",
    ".venv",
    "tests",
    "services/bramhastra/data",
    "__pycache__",
    "src/database/migrations",
]
EXEC_FILES, IMPORT_FILES = get_py_files(ROOT_DIR, dirs_to_ignore)

if IMPORT_FILES:
    for f in IMPORT_FILES:
        f = f.replace("/", ".")
        EXEC_LINES.append(f"from {f[:-3]} import *")


@click.group()
def envision_cli():
    pass


@envision_cli.group("server")
def envision_server():
    pass


@envision_server.command("develop")
def run_development_server(port: int = 8000):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", port))
            sock.close()
            break
        except OSError:
            port += 1
    if port != 8000:
        print(f"Starting server on http://127.0.0.1:{port}/")
        user_input = input("Press 'y' to continue or any other key to quit: ")
        if user_input.lower() != "y":
            return
    uvicorn.run("main:app", reload=True, port=port)


@envision_server.command("shell")
@click.argument("ipython_args", nargs=-1, type=click.UNPROCESSED)
def shell(ipython_args):
    import sys
    import IPython
    from IPython.terminal.ipapp import load_default_config
    from database.db_session import db

    config = load_default_config()
    config.TerminalInteractiveShell.banner1 = (
        f"""Python {sys.version} on {sys.platform} IPython: {IPython.__version__}"""
    )
    config.TerminalInteractiveShell.autoindent = True
    config.InteractiveShellApp.exec_lines = EXEC_LINES
    config.InteractiveShellApp.exec_files = EXEC_FILES
    config.TerminalInteractiveShell.autoformatter = 'black'
    config.InteractiveShell.pdb = True
    VerboseTB._tb_highlight = "bg:#4C5656"
    config.InteractiveShell.ast_node_interactivity = "all"
    config.InteractiveShell.debug = True
    user_ns = {"database": db}
    with db.connection_context():
        IPython.start_ipython(argv=ipython_args, user_ns=user_ns, config=config)


envision_server.add_command(uvicorn.main, name="start")


def entrypoint():
    try:
        envision_cli()
    except Exception as e:
        click.secho(f"ERROR: {e}", bold=True, fg="red")


if __name__ == "__main__":
    entrypoint()

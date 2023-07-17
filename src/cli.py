import click
import uvicorn
import socket

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
    uvicorn.run("main:app", reload=True,port = port)
    
@envision_server.command("shell")
@click.argument("ipython_args", nargs=-1, type=click.UNPROCESSED)
def shell(ipython_args):
    import sys
    import IPython
    from IPython.terminal.ipapp import load_default_config
    from database.db_session import db
    config = load_default_config()
    config.TerminalInteractiveShell.banner1 = f"""Python {sys.version} on {sys.platform} IPython: {IPython.__version__}"""
    config.InteractiveShellApp.exec_lines = ['%load_ext autoreload','%autoreload 2']
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
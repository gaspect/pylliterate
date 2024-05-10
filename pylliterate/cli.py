# !!! info "This module contains the pylliterate CLI application."
#     The CLI application is basically a [Typer](https://typer.tiangolo.com) application
#     with three commands, that manage the whole process.

# The pylliterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with three commands.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.


import typer

# These two are for watching file changes.

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# And these are internal.

from pylliterate import process_all, process
from pylliterate.config import PylliterateConfig

# These are the types for our arguments, and `shutil` for copying files.

from pathlib import Path
from typing import List

# We start by creating the main typer application and a set of related commands.
app = typer.Typer()


# ## Command helpers

# We use a decorator to bookkeeping common code between all commands

def configurable(fn):
    def command(
            src: List[str] = typer.Option([]),
            inline: bool = False,
            linenums: bool = False,
            highlights: bool = False,
            title: bool = False,
            config: Path = None,
    ):
        try:
            cfg = PylliterateConfig.load(src, inline, linenums, highlights, title, config)
            return fn(cfg)
        except PylliterateConfig.ConfigurationNotProvidedException as e:
            typer.echo(str(e))
            typer.Exit(code=1)
    return command


# ## The build command

# Here is the implementation of the build command
# is called when `python -m pylliterate build` is used.
# This command parse and creates the documentation based on its input parameters.


@app.command("build")
@configurable
def build(config: PylliterateConfig):
    process_all(config)


# ## The config command
#
# > we named it konfig to avoid clashes with config parameter and shadowing

@app.command("config")
@configurable
def konfig(config: PylliterateConfig):
    print(config)


# ## The watching system
#
# With `watchdog` we need to define a class that hold the logic to be executed when filesystem change
# the PylliterateHandler class fulfil that purpose
class PylliterateHandler(FileSystemEventHandler):
    def __init__(
            self, input_path: Path, output_path: Path, cfg: PylliterateConfig
    ) -> None:
        super().__init__()
        self.cfg = cfg
        self.input_path = input_path
        self.output_path = output_path

    def on_modified(self, event: FileModifiedEvent):
        typer.echo(f"Recreating: {self.input_path} -> {self.output_path}")
        process(self.input_path, self.output_path, self.cfg)


# Then we add a command (maybe a flag in the needed command is just a better idea) that set up the watchdog observer
# mechanism over filesystem using our handler
@app.command("watch")
@configurable
def watch(config: PylliterateConfig):
    process_all(config)
    observer = Observer()

    for input_path, output_path in config.files:
        observer.schedule(
            PylliterateHandler(input_path, output_path, config), input_path
        )

    observer.start()
    observer.join()

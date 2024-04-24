# !!! info "This module contains the pylliterate CLI application."
# The CLI application is basically a [Typer](https://typer.tiangolo.com) application
# with three commands, that manage the whole process.


# The pylliterate CLI app is a very simple [Typer](https://typer.tiangolo.com)
# application with three commands.
# Typer is a CLI creation tool where you define commands as methods,
# and it takes advantage of Python type annotations to provide argument parsing
# and documentation.


import typer
import yaml

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

# Most of the commands will take either CLI args or a --config file. So we will define a private function to take
# care of configuration load  either from a specified configuration file or using default values and parameters provided


def _load_config(src, inline, linenums, highlights, title, config):
    if config:
        with config.open() as fp:
            cfg = PylliterateConfig(**yaml.safe_load(fp))
    elif not src and Path("pylliterate.yml").exists():
        with open("pylliterate.yml") as fp:
            cfg = PylliterateConfig(**yaml.safe_load(fp))
    else:
        if not src:
            typer.echo("At least one source or a config file must be provided.")
            raise typer.Exit(1)
        cfg = PylliterateConfig.make(sources=src, inline=inline, linenums=linenums,
                                     highlights=highlights, title=title)
    return cfg


# Then we use a decorator to bookkeeping common code between all commands

def pylliterate_command(fn):
    def command(
            src: List[str] = typer.Option([]),
            inline: bool = False,
            linenums: bool = False,
            highlights: bool = False,
            title: bool = False,
            config: Path = None,
    ):
        cfg = _load_config(src, inline, linenums, highlights, title, config)
        return fn(cfg)

    return command


# ## The build command

# Here is the implementation of the build command
# is called when `python -m pylliterate build` is used.
# This command parse and creates the documentation based on its input parameters.


@app.command("build")
@pylliterate_command
def build(config: PylliterateConfig):
    process_all(config)


# ## The config command


@app.command("config")
@pylliterate_command
def config(config: PylliterateConfig):
    print(yaml.safe_dump(config.dict()))


class IlliterateHandler(FileSystemEventHandler):
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


@app.command("watch")
@pylliterate_command
def watch(config: PylliterateConfig):
    process_all(config)
    observer = Observer()

    for input_path, output_path in config.files:
        observer.schedule(
            IlliterateHandler(input_path, output_path, config), input_path
        )

    observer.start()
    observer.join()


# ## Processing a config file

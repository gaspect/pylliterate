# !!! info "This module contains the pylliterate configuration class"
#     The configuration class is a mapper between user define configuration and a python object.


# We start as usually,  importing necessary modules

import logging
from functools import cached_property
from pathlib import Path
import yaml
from typing import Dict
from pydantic import BaseModel

logger = logging.getLogger("pylliterate")


# ## The configuration class
#
# We define a configuration class for Pylliterate using Pydantic BaseModel for proper
# auto mapping and validation. We took a KISS and single responsibility approach binding all configuration related
# logic to this class instead of build an anemic POJO class

class PylliterateConfig(BaseModel):
    # 'inline' specifies if the documentation is shown inline within the source code
    inline: bool = False

    # 'title' specifies if headings/titles should be created in the documentation
    title: bool = False

    # 'linenums' specifies if line numbers should be included in the documentation
    linenums: bool = False

    # 'highlights' specifies if code snippets should be highlighted
    highlights: bool = False

    # sources is a dictionary mapping source file paths to their respective documentation file paths
    sources: Dict[str, str]

    # A class error bound to this class because `only this class can throw that error`, is the error threw when
    # pylliterate configuration isn't provided

    class ConfigurationNotProvidedException(Exception):
        def __init__(self):
            super().__init__("At least one source or a config file must be provided.")

    # We need a class method that creates an instance of PylliterateConfig
    # from a list of source files and other options, the make method fulfill goal
    @classmethod
    def load(cls, src, inline, linenums, highlights, title, config) -> "PylliterateConfig":
        if config:
            with config.open() as fp:
                cfg = cls(**yaml.safe_load(fp))
        elif not src and Path("pylliterate.yml").exists():
            with open("pylliterate.yml") as fp:
                cfg = cls(**yaml.safe_load(fp))
        else:
            if not src:
                raise cls.ConfigurationNotProvidedException()
            sources = {}

            # iterate over every source line
            for line in src:
                # split the line into the input file path and output file path
                i, o = line.split(":")
                # add the input and output paths to the dictionary
                sources[i] = o

            # return an instance of PylliterateConfig with the specified sources and options
            cfg = cls(sources=sources, inline=inline, linenums=linenums,
                      highlights=highlights, title=title)
        return cfg

    # Since the sources attribute is a user-friendly representation of the file system,
    # we need to process it in order to use it correctly. That's what the property files does.

    @cached_property
    def files(self):
        # iterate over all items (input and output paths) in the sources dictionary
        for input_path, output_path in self.sources.items():
            # yield a tuple of Path objects for the input source file and its corresponding documentation file
            in_path, out_path = Path(input_path).resolve(), Path(output_path).resolve()

            # if the input path if a directory we try to expand it
            if in_path.is_dir() and out_path.is_dir():
                for file in in_path.rglob("*.py"):
                    yield (in_path / file.relative_to(in_path)), (
                            out_path / in_path.relative_to(Path.cwd()) / str(file.relative_to(in_path))
                            .replace(".py", ".md"))
            elif in_path.is_file():
                yield in_path, out_path
            else:
                logger.warning(f"Improper input or output path for {in_path} and {out_path}.")

    def __str__(self):
        return yaml.safe_dump(self.dict())

# !!! info "This module contains the pylliterate configuration class"
# The configuration class is a mapper between user define configuration and a python object.


# We start as usually,  importing necessary modules

import logging
from functools import cached_property
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel

logger = logging.getLogger("pylliterate")

# ## The configuration class
# We define a configuration class for Pylliterate using Pydantic's BaseModel for proper auto mapping and validation

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

    # We need a class method that creates an instance of PylliterateConfig
    # from a list of source files and other options, the make method fulfill goal
    @classmethod
    def make(cls, *, sources: List[str], **kwargs):
        # initialize empty dictionary
        source_dict = {}

        # iterate over every source line
        for line in sources:
            # split the line into the input file path and output file path
            input, output = line.split(":")
            # add the input and output paths to the dictionary
            source_dict[input] = output

        # return an instance of PylliterateConfig with the specified sources and options
        return cls(sources=source_dict, **kwargs)

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
                    yield (in_path / file.relative_to(in_path)), (out_path / in_path.relative_to(Path.cwd()) / str(file.relative_to(in_path))
                                                                  .replace(".py", ".md"))
            elif in_path.is_file():
                print(in_path, out_path)
                yield in_path, out_path
            else:
                logger.warning(f"Improper input or output path for {in_path} and {out_path}.")

# This module simply allows calling pylliterate as
# `python -m pylliterate`.
# We just import the CLI app and set up the right name so
# that documentation is correct.


from .cli import app

if __name__ == "__main__":
    app(prog_name="python -m pylliterate")

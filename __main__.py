#!/usr/bin/env python3
"""The main entry point to the translator"""
from argparse import ArgumentParser
from pathlib import Path
import sys

from pythonlua.translator import Translator


def create_arg_parser():
    """Create and initialize an argument parser object"""
    parser = ArgumentParser(description="Python to lua translator.")
    parser.add_argument("inputfilename", metavar="IF", type=str,
                        help="A python script filename to translate it.")

    return parser


def main():
    """Entry point function to the translator"""
    parser = create_arg_parser()
    argv = parser.parse_args()

    input_filename = argv.inputfilename
    if not Path(input_filename).is_file():
        raise RuntimeError(
            "The given filename ('{}') is not a file.".format(input_filename))

    content = None
    with open(input_filename, "r") as file:
        content = file.read()

    if not content:
        raise RuntimeError("The input file is empty.")

    translator = Translator()
    lua_code = translator.translate(content)

    print(translator.get_luainit())
    print(lua_code)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""The main entry point to the translator"""
from argparse import ArgumentParser
from pathlib import Path
import sys

from pythonlua.config import Config
from pythonlua.translator import Translator


def create_arg_parser():
    """Create and initialize an argument parser object"""
    parser = ArgumentParser(description="Python to lua translator.")
    parser.add_argument("inputfilename", metavar="IF", type=str,
                        help="A python script filename to translate it.",
                        nargs="?", default="")
    parser.add_argument("configfilename", metavar="CONFIG", type=str,
                        help="Translator configuration file in yaml format.",
                        nargs="?", default=".pyluaconf.yaml")

    parser.add_argument("--show-ast", help="Print python ast tree before code.",
                        dest="show_ast", action="store_true")
    parser.add_argument("--only-lua-init", help="Print only lua initialization code.",
                        dest="only_lua_init", action="store_true")
    parser.add_argument("--no-lua-init", help="Print lua code without lua init code.",
                        dest="no_lua_init", action="store_true")

    return parser


def main():
    """Entry point function to the translator"""
    parser = create_arg_parser()
    argv = parser.parse_args()

    if not argv.no_lua_init:
        print(Translator.get_luainit())

    if argv.only_lua_init:
        return 0

    input_filename = argv.inputfilename
    if not Path(input_filename).is_file():
        raise RuntimeError(
            "The given filename ('{}') is not a file.".format(input_filename))

    content = None
    with open(input_filename, "r") as file:
        content = file.read()

    if not content:
        raise RuntimeError("The input file is empty.")

    translator = Translator(Config(argv.configfilename),
                            show_ast=argv.show_ast)
    lua_code = translator.translate(content)

    if not argv.only_lua_init:
        print(lua_code)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Run all tests from the tests folder"""
import os
import re
import subprocess
import sys
import tempfile

from colorama import init, Fore, Style

from pythonlua.translator import Translator


TESTS_FOLDER = "tests"
LUA_PATH = "lua"

EXPECTED_FORMAT = "{}.expected"


def get_all_tests(folder):
    """Get all test filenames"""
    filenames = [os.path.join(folder, f) for f in os.listdir(folder)
                 if re.match(r".*\.py$", f)]

    for fname in filenames:
        test_name = fname
        expected = EXPECTED_FORMAT.format(test_name)
        if not os.path.isfile(fname):
            raise RuntimeError("Object '{}' is not a file.".format(test_name))
        if not os.path.isfile(expected):
            raise RuntimeError("Expected output in a file '{}'.".format(expected))
    return filenames


def make_test(filename):
    """Make test"""
    print("Testing file: {}".format(filename), end=" ")

    content = None
    expected = None

    with open(filename) as file:
        content = file.read()
    with open(EXPECTED_FORMAT.format(filename)) as file:
        expected = file.read()

    if content is None or expected is None:
        return False

    result = None

    try:
        translator = Translator()
        lua_code = translator.translate(content)

        tmp_file = tempfile.NamedTemporaryFile("w")
        tmp_file.write(lua_code)
        tmp_file.flush()

        output = []

        proc = subprocess.Popen([LUA_PATH, tmp_file.name],
                                stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if line == b"":
                break
            else:
                output.append(line.decode("utf-8"))

        output = "".join(output)

        result = output == expected
    except RuntimeError:
        result = False

    print(Fore.GREEN + "PASSED" if result else Fore.RED + "FAILED")
    print(Style.RESET_ALL, end="")
    return result


def main():
    """Main tests entrypoint"""
    init()

    tests = get_all_tests(TESTS_FOLDER)

    passed = 0

    for test in tests:
        if make_test(test):
            passed += 1

    print("=" * 80)
    print("Passed: {}/{}".format(passed, len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
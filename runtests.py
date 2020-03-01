#!/usr/bin/env python3
"""Run all tests from the tests folder"""
import os
import re
import subprocess
import sys

from tempfile import mkstemp

from colorama import init, Fore, Style

from pythonlua.translator import Translator


TESTS_FOLDER = "tests"
LUA_PATH = "lua53"

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
    readme = '''
### {}
<details><summary>Open</summary>
<p>
Python code:

```python
{}
```
</p>
'''.format(filename[6:-3].title(),content)
    try:
        translator = Translator()
        lua_code = translator.translate(content)
        readme += '''<p>
Lua code:

```lua
{}
```
</p>
'''.format(lua_code)
        file_desc, filename = mkstemp()

        tmp_file = os.fdopen(file_desc, "w")
        tmp_file.write(Translator.get_luainit()+ "\n")
        tmp_file.write(lua_code)
        tmp_file.flush()
        tmp_file.close()

        output = []

        proc = subprocess.Popen([LUA_PATH, filename],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,)
        while True:
            line = proc.stdout.readline()
            if line == b"":
                break
            else:
                output.append(line.decode("utf-8"))
        # while True:
        #     line = proc.stderr.readline()
        #     if line == b"":
        #         break
        #     else:
        #         output.append(line.decode("utf-8"))
        output = "".join(output)
        readme += '''<p>
Output:

{}
</p>
</details>
'''.format(output.replace('\n','\n'))
        os.remove(filename)

        output = [item.strip() for item in output.split("\n")]
        expected = [item.strip() for item in expected.split("\n")]

        if output != expected:
            print("output: ", output)
            print("expected: ", expected)
            print("for lua code: \n{}\n".format(lua_code))


        result = output == expected
    except RuntimeError:
        result = False
    with open('readme.txt','a') as f:
        f.write(readme)
    print(Fore.GREEN + "PASSED" if result else Fore.RED + "FAILED")
    print(Style.RESET_ALL, end="")
    return result


def main():
    """Main tests entrypoint"""
    init()

    tests = get_all_tests(TESTS_FOLDER)

    passed = 0
    with open('readme.txt','w') as f:
        f.write('')
    for test in tests:
        if make_test(test):
            passed += 1

    print("=" * 80)
    print("Passed: {}/{}".format(passed, len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
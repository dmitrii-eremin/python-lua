#!/usr/bin/env python3
"""Module setup utils"""

from setuptools import setup, find_packages

setup(
    name="pythonlua",
    version="1.2.0",
    url="https://github.com/Blimba/python-lua",
    author="Eremin Dmitry, Bart Limburg",
    author_email="mail@eremindmitry.ru, bartlimburg@gmail.com",
    licence="Apache",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'pythonlua/luainit.lua']},
    include_package_data=True,
    long_description="",
)
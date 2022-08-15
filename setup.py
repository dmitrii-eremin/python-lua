#!/usr/bin/env python3
"""Module setup utils"""

from setuptools import setup, find_packages

setup(
    name="pythonlua",
    version="1.0",
    url="https://github.com/NeonMercury/python-lua",
    author="Eremin Dmitry",
    author_email="mail@eremindmitry.ru",
    license="Apache 2.0",
    python_requires=">=3.4",
    packages=find_packages(include=['pythonlua', 'pythonlua.*']),
    long_description="",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "python-lua = pythonlua.__main__:main",
        ],
    }
)

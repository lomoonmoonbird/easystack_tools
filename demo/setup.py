#encoding:utf-8
from setuptools import setup
from setuptools import find_packages

setup(
    name = "cmdline",
    version = 1.0,
    description = "Command line Demo",
    author = "moonmoonbird",
    packages = find_packages(),
    platforms = "any",
    install_requires = [        "requests",
        "docopt>=0.6.2"
    ],
    entry_points = {        "console_scripts": ['clidemo = demo.cmdline:cmd']
    }
)
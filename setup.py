"""Packaging settings."""


from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from xarta import __version__

# Get the long description from the README file
this_dir = abspath(dirname(__file__))
with open(join(this_dir, "README.md"), encoding="utf-8") as file:
    long_description = file.read()

# get the dependencies and installs
with open(join(this_dir, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

class RunTests(Command):
    """Run all tests."""

    description = "run tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(["py.test", "--cov=xarta", "--cov-report=term-missing"])
        raise SystemExit(errno)


setup(
    name="xarta",
    version=__version__,
    description="A command-line tool for organising papers from the arXiv.",
    long_description=long_description,
    url="https://github.com/johngarg/xarta",
    author="John Gargalionis",
    author_email="johngargalionis@gmail.com",
    license="UNLICENSE",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: Public Domain",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    keywords="cli",
    packages=find_packages(exclude=["docs", "tests*"]),
    install_requires=install_requires,
    dependency_links=dependency_links,
    extras_require={"test": ["coverage", "pytest", "pytest-cov"],},
    entry_points={"console_scripts": ["xarta=xarta.cli:main",],},
    cmdclass={"test": RunTests},
)

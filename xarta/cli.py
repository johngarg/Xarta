"""
xarta

Usage:
  xarta hello
  xarta init <database-location>
  xarta open <ref> [--pdf]
  xarta add <ref> [--tag=<tg>]...
  xarta -h | --help
  xarta --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --pdf                             Open the pdf.
  --tag=<tg>                        Add tag metadata to the database entry.

Examples:
  xarta hello
  xarta open 1704.05849
  xarta open 1704.05849 --pdf
  xarta open hep-ph
  xarta add 1704.05849 --tag leptoquarks --tag neutrino-mass --tag flavour-anomalies

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/johngarg/xarta
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import xarta.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items(): 
        if hasattr(xarta.commands, k) and v:
            module = getattr(xarta.commands, k)
            xarta.commands = getmembers(module, isclass)
            command = [command[1] for command in xarta.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()

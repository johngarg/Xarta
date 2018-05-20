"""
xarta

Usage:
  xarta hello
  xarta init <database-location>
  xarta open <ref> [--pdf]
  xarta add <ref> [--tag=<tg>]... [--download] [--local]
  xarta delete <ref>
  xarta browse [--all] [--author=<auth>] [--tag=<tg>]... [--title=<ttl>] [--ref=<ref>] [--category=<cat>]
  xarta export <export-path> [--tag=<tg>]... [--bibtex]
  xarta -h | --help
  xarta --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --pdf                             Open the pdf.
  --tag=<tg>                        Tag metadata of the database entry.
  --author=<auth>                   Author metadata of the database entry.
  --title=<ttl>                     Title metadata of the database entry.
  --bibtex                          Option to export bibliography to bibtex file.
  --download                        Option to save file locally for offline reading.
  --local                           Option to add an already locally saved file to database.

Examples:
  xarta open 1704.05849
  xarta open 1704.05849 --pdf
  xarta open hep-ph
  xarta add 1704.05849 --tag leptoquarks --tag neutrino-mass --tag flavour-anomalies
  xarta remove 1704.05849
  xarta browse --tag neutrino-mass
  xarta export ~/Desktop/ --bibtex

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/johngarg/Xarta
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

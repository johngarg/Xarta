"""
xarta

Usage:
  xarta hello
  xarta init <database-location>
  xarta open <ref> [--pdf]
  xarta add <ref> [<tags> ...]
  xarta delete <ref>
  xarta edit <ref> [<tags> ...]
  xarta browse [--all] [--author=<auth>] [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>] [<tags> ...]
  xarta lucky [--author=<auth>] [--title=<ttl>] [--pdf] [<tags> ...]
  xarta choose [--author=<auth>] [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>] [--pdf] [<tags> ...]
  xarta info <ref>
  xarta list <obj> [--contains=<cont>]
  xarta export <export-path> [--bibtex] [<tags> ...]
  xarta -h | --help
  xarta --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --pdf                             Open the pdf.
  --author=<auth>                   Author metadata of the database entry.
  --title=<ttl>                     Title metadata of the database entry.
  --bibtex                          Option to export bibliography to bibtex file.
  --download                        Option to save file locally for offline reading.
  --local                           Option to add an already locally saved file to database.
  --filter=<fltr>                   Filter results using python logic statements. See Examples.


The available commands are:
  init                              Initialises the paper database in a given directory. The database directory is stored in ~/.xarta.
  add                               Add an arXiv ID, optionally with some tags.
  delete                            Remove and arXiv ID.
  open                              Opens the abstract or pdf url of a paper.
  browse                            Searches for and prints matching papers in the database
  list                              Lists tags or authors, optionally print only those containing some substring
With the exception of the --filter option, all search conditions are connected by logical disjunction.

Examples:
  xarta open 1704.05849
  xarta open 1704.05849 --pdf
  xarta open hep-ph
  xarta add 1704.05849 leptoquarks neutrino-mass flavour-anomalies
  xarta browse neutrino-mass
  xarta browse --filter="'John' in authors and ('neutrino' in tags or 'leptoquarks' in tags)"
  xarta remove 1704.05849
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
            command = [
                command[1] for command in xarta.commands if command[0] != "Base"
            ][0]
            command = command(options)
            command.run()

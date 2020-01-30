"""
xarta


Usage:
  xarta hello
  xarta open <ref> [--pdf]
  xarta init [<database-location>]
  xarta add <ref> [<tag> ...]
  xarta delete <ref>
  xarta info <ref>
  xarta choose [--author=<auth>] [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>] [--pdf] [<tag> ...]
  xarta lucky [--author=<auth>] [--title=<ttl>] [--pdf] [<tag> ...]
  xarta browse [--author=<auth>] [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>] [<tag> ...]
  xarta list (authors|tags) [--contains=<cont>]
  xarta export <export-path> [<tag> ...]
  xarta edit <ref> [--action=<act>] [<tag> ...]
  xarta -h | --help
  xarta --version


Command descriptions:
  open                              Opens the abstract or pdf url of an arXiv ID, or an arXiv category's new submissions page. The paper does not need to be in the database.
  init                              Initialises the xarta database in '<database-location>/.xarta.d'. The location of the database is written to '~/.xarta'.
  add                               Add an arXiv ID, optionally with some tags.
  delete                            Remove and arXiv ID.
  edit                              Updates the tags of a paper.
  info                              Displays information about a paper. Unlike 'xarta open', the paper must be in the database.
  choose                            Choose a paper to open from a list of papers matching some criteria.
  lucky                             Randomly choose a paper to open from a list of papers matching some criteria.
  browse                            Prints all papers, optionally showing only those matching some criteria.
  list                              Lists authors or tags, optionally print only those containing some substring
  export                            Exports libtrary to a bibtex bibliography.
  edit                              Set, add, or delete tags.
With the exception of the --filter option, all search conditions are connected by logical disjunction.


Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --pdf                             Open the pdf url, as opposed to the abstract url.
  --author=<auth>                   Author metadata of the database entry.
  --title=<ttl>                     Title metadata of the database entry.
  --download                        Option to save file locally for offline reading.
  --local                           Option to add an already locally saved file to database.
  --filter=<fltr>                   Filter results using python logic statements. See Examples.
  --action=<act>                    Edit action, either 'set', 'add', or 'delete' tags [default: set]


Examples:
  xarta open 1704.05849
  xarta open 1704.05849 --pdf
  xarta open hep-ph
  xarta add 1704.05849 leptoquarks neutrino-mass flavour-anomalies
  xarta browse
  xarta browse neutrino-mass
  xarta browse --filter="'John' in authors and ('neutrino' in tags or 'leptoquarks' in tags)"
  xarta list tags
  xarta list authors
  xarta export ~/Desktop
  xarta delete 1704.05849


Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/johngarg/Xarta
"""

import sys

from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION

from .utils import XartaError, is_valid_ref, process_ref


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

            # process and check validity of any arxiv IDs
            for opt in ["<ref>", "--ref"]:
                if options[opt]:
                    options[opt] = process_ref(options[opt])
                    if not is_valid_ref(options[opt]):
                        print("Not a valid arXiv reference: " + options[opt])
                        sys.exit(1)

            command = command(options)
            try:
                command.run()
            except XartaError as err:
                # Error is of type XartaError, an 'expected' error due to bad user input. Print the error.
                print(str(err))

"""
xarta


Usage:
  xarta hello
  xarta open <ref> [--pdf]
  xarta init <database-location>
  xarta add <ref> [--alias=<alias>] [<tag> ...]
  xarta delete <ref>
  xarta info <ref>
  xarta choose [--author=<auth>] [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>] [--pdf] [<tag> ...]
  xarta lucky [--author=<auth>] [--title=<ttl>] [--pdf] [<tag> ...]
  xarta browse [--author=<auth>] [--title=<ttl>] [--ref=<ref>] [--category=<cat>] [--filter=<fltr>] [<tag> ...]
  xarta list (authors|tags|aliases) [--contains=<cont>]
  xarta export <export-path> [<tag> ...]
  xarta edit <ref> [--action=<act>] [<tag> ...]
  xarta alias <ref> [<alias>]
  xarta rename <tag> [<tag>]
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
  list                              Lists authors, tags, or aliases. Optionally print only those containing some substring
  export                            Exports libtrary to a bibtex bibliography.
  edit                              Set, add, or delete tags.
  alias                             Set an alias. if no <alias> argument given, clear alias.
  rename                            Rename or delete a tag throughout the database
With the exception of the --filter option, all search conditions are connected by logical disjunction.


Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --pdf                             Open the pdf url, as opposed to the abstract url.
  --author=<auth>                   Author metadata of the database entry.
  --title=<ttl>                     Title metadata of the database entry.
  --local                           Option to add an already locally saved file to database.
  --filter=<fltr>                   Filter results using python logic statements. See Examples.
  --action=<act>                    Edit action, either 'set', 'add', or 'delete' tags [default: set]


Examples:
  xarta open 1704.05849
  xarta open 1704.05849 --pdf
  xarta open hep-ph
  xarta add 1704.05849 leptosquark neutrino-mass flavour-anomalies
  xarta rename leptosquark leptoquarks
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


from inspect import ismodule

from docopt import docopt

from . import __version__ as VERSION

from .utils import XartaError


def main():
    """Main CLI entrypoint."""
    import xarta.commands

    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if v and hasattr(xarta.commands, k) and ismodule(getattr(xarta.commands, k)):
            # key corresponds to a module in xarta.commands.
            # obtain the command_class associated with that module
            command_module = getattr(xarta.commands, k)
            command_class = getattr(command_module, k.capitalize())
            # If the naming convention of classes is UpperCamelCase, what is the
            # convention for variables that point TO a class?

            try:
                command = command_class(options)
                command.run()
            except XartaError as err:
                print(str(err))

"""xarta


Usage:
  xarta hello
  xarta open <ref> [--pdf]
  xarta init [<database-file>]
  xarta add <ref> [--alias=<alias>] [<tag> ...]
  xarta delete <ref>
  xarta info <ref>
  xarta browse [--author=<auth>] [--title=<ttl>] [--ref=<ref>]
               [--category=<cat>] [--filter=<fltr>] [<tag> ...]
  xarta choose [--author=<auth>] [--title=<ttl>] [--ref=<ref>]
               [--category=<cat>] [--filter=<fltr>] [--pdf] [<tag> ...]
  xarta export (arxiv|inspire) <bibtex-file> [--export-alias] [--author=<auth>]
               [--title=<ttl>] [--ref=<ref>] [--category=<cat>]
               [--filter=<fltr>] [<tag> ...]
  xarta list (authors|tags|aliases) [--sort=<order>] [--contains=<cont>]
  xarta lucky [--author=<auth>] [--title=<ttl>] [--pdf] [<tag> ...]
  xarta tags (set|add|remove) <ref> [<tag> ...]
  xarta alias <ref> [<alias>]
  xarta rename <tag> [<tag>]
  xarta refresh <ref>
  xarta -h | --help
  xarta --version



Command descriptions:

  open         Opens the abstract or pdf url of an arXiv ID, or an arXiv
               category's new submissions page. The paper does not need to be
               in the database.

  init         Initialise and write the xarta database to '<database-file>'. The
               database path is stored in a config file whoose path is either
               '$XARTACONFIG', '$XDG_HOME_CONFIG/xarta.conf', or
               '$HOME/.xarta.conf'. If no option is given, the database is
               written to 'xarta.db' in the same folder as the config file.

  add          Add an arXiv ID, optionally with some tags.

  delete       Remove and arXiv ID.

  tags         Updates the tags associated with a paper.

  info         Displays information about a paper. Unlike 'xarta open', the
               paper must be in the database.

  browse       Prints all papers, optionally showing only those matching some
               criteria.

  choose       Choose a paper to open from a list of papers matching some
               criteria. Arguments mostly the same as browse.

  export       Exports libary to a bibtex bibliography. Bibtex information comes
               from either arxiv (crosref) or inspire. The --export-alias option
               will insert an ids field containing the arxiv id and alias into
               the bibtex entries, for use with biblatex and biber. Papers to be
               exported can be selected using the same arguments as the browse
               command.

  list         Lists authors, tags, or aliases. Can be sorted by date,
               alphabetically, or by number of papers. Optionally print only
               results containing some substring.

  lucky        Randomly choose a paper to open from a list of papers matching
               some criteria.

  tags         Set, add, or remove tags.

  alias        Set an alias for a paper. if no <alias> argument given, clear
               alias. Aliases can be used in place of arXiv references.

  rename       Rename a tag throughout the database, or delete it if no new
               tag is provided.

  refresh      Refreshes database information for a given paper. Usefull if a
               new arxiv version was released.

With the exception of the --filter option, all search conditions are connected
by logical disjunction.



Options:
  -h --help               Show this screen.
  --version               Show version.
  --pdf                   Open the pdf url, as opposed to the abstract url.
  --author=<auth>         Searches author metadata of the database entry.
  --title=<ttl>           Searches title metadata of the database entry.
  --filter=<fltr>         Filter results using python logic. See Examples.
  --sort=<order>          Order to sort lists. Can be sorted by 'date-added',
                          'alphabetical', or by the 'number' of papers,
                          [default: alphabetical]


Examples:
  xarta open 1704.05849
  xarta open 1704.05849 --pdf
  xarta open hep-ph
  xarta add 1704.05849 leptosquark neutrino-mass flavour-anomalies
  xarta tags add 1704.05849 self_author
  xarta rename leptosquark leptoquarks
  xarta browse
  xarta browse neutrino-mass
  xarta browse --filter="'John' in authors or 'Reconsidering' in title"
  xarta browse --filter='"1704" in ref and ("trino" in tags or "lepto" in tags)'
  xarta choose --filter='"John" in authors and "hep-ph" in category'
  xarta list tags
  xarta list authors
  xarta export ~/Desktop/xarta.bib --author='John'
  xarta delete 1704.05849


Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/johngarg/Xarta

"""

import sys

from inspect import ismodule

from docopt import docopt

from . import __version__ as VERSION

from .utils import XartaError


def main():
    """Main CLI entrypoint."""
    import xarta.commands

    options = docopt(__doc__, version=VERSION)

    # some commands are also options now, e.g., 'xarta add' and 'xarta tags
    # add'. to avoid confusion, first argument,  not options, to determine command
    first_arg = sys.argv[1]

    if hasattr(xarta.commands, first_arg) and ismodule(
        getattr(xarta.commands, first_arg)
    ):
        # first_arg corresponds to a module in xarta.commands.
        # obtain the command_class associated with that module
        command_module = getattr(xarta.commands, first_arg)
        command_class = getattr(command_module, first_arg.capitalize())
        # If the naming convention of classes is UpperCamelCase, what is the
        # convention for variables that point TO a class?

        try:
            command = command_class(options)
            command.run()
        except XartaError as err:
            print(str(err))
            # return exit with error
            sys.exit(1)

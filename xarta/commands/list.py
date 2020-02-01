"""The list command."""

from collections import namedtuple
from .base import BaseCommand
from ..database import PaperDatabase, DATA_HEADERS
from ..utils import XartaError, string_to_list

Paper = namedtuple("Paper", DATA_HEADERS)


class List(BaseCommand):
    """ List all tags or authors in library. """

    def run(self):
        options = self.options
        cont = options["--contains"]

        if options["tags"]:
            column = "tags"
        elif options["authors"]:
            column = "authors"
        elif options["aliases"]:
            column = "alias"
        else:
            raise XartaError("Xarta list only lists tags, authors, or aliases.")

        with PaperDatabase(self.database_path) as paper_database:
            tuple_data = paper_database.get_all_papers()
            namedtuple_data = map(lambda x: Paper(*x), tuple_data)
            items = set([])
            for paper in namedtuple_data:
                string_list = getattr(paper, column)
                list_ = string_to_list(string_list)
                for item in list_:
                    if item:  # dont print empty tags/aliases
                        items.add(item)

            for item in sorted(list(items)):
                if cont is None:
                    print(item)
                elif cont in item:
                    print(item)

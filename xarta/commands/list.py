"""The list command."""

from collections import namedtuple
from .base import BaseCommand
from ..database import PaperDatabase, DATA_HEADERS
from ..utils import XartaError

Paper = namedtuple("Paper", DATA_HEADERS)


class List(BaseCommand):
    """ List all tags or authors in library. """

    def run(self):
        options = self.options
        tags = options["tags"]
        authors = options["authors"]
        aliases = options["aliases"]
        cont = options["--contains"]

        if tags:
            column = "Tags"
        elif authors:
            column = "Authors"
        elif aliases:
            column = "Alias"
        else:
            raise XartaError("Xarta list only lists tags, authors, or aliases.")

        with PaperDatabase() as paper_database:
            tuple_data = paper_database.get_all_papers()
            namedtuple_data = map(lambda x: Paper(*x), tuple_data)
            items = set([])
            for paper in namedtuple_data:
                string_list = getattr(paper, column)
                list_ = [s.strip() for s in string_list.split(";")]
                for item in list_:
                    if item:  # dont print empty tags/aliases
                        items.add(item)

            for item in sorted(list(items)):
                if cont is None:
                    print(item)
                elif cont in item:
                    print(item)

"""The list command."""

from collections import namedtuple
from .base import BaseCommand
from ..database import PaperDatabase, DATA_HEADERS
from ..utils import XartaError, string_to_list


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

        order = options["--sort"]
        if not order in ["alphabetical", "date-added", "number"]:
            raise XartaError(
                "Sorting order must be either 'alphabetical', 'date-added', or 'number'."
            )

        if order != "alphabetical" and column == "alias":
            raise XartaError("Aliases can only be sorted alphabetically.")

        with PaperDatabase(self.database_path) as paper_database:
            papers = paper_database.get_all_papers()

        # get data of interest from list of papers
        items = []
        for paper in papers:
            index = DATA_HEADERS.index(column)
            string_list = paper[index]
            list_ = string_to_list(string_list)
            for item in list_:
                if item:  # dont print empty tags/aliases
                    items.append(item)

        # time to start sorting!

        if order == "alphabetical":
            # remove duplicated
            data = list(set(items))

            # sort alphabetically
            data = sorted(data)

        if order == "number":
            # First sord by alphabet (tie-breaker)
            items = sorted(items)

            # then sort by number of occurrences
            items = sorted(items, key=items.count, reverse=True)

            # then get list of unique elements alognside their number of
            # appearances. Note that we cannot use set() as it has no concept of
            # ordering.

            data = []
            count = []
            for datum in items:
                if not datum in data:
                    data.append(datum)
                    count.append(items.count(datum))

        if order == "date-added":
            # Already in order by virtue of database retrival. Just have to
            # ensure data is unique. However, sets have no concepts of order,
            # need to do so manyall.
            data = []
            for datum in items:
                if datum not in data:
                    data.append(datum)

        name = "aliases" if column == "alias" else column
        # finnally print!
        if order != "number":
            # just print desired fields
            print("List of " + name + ":")
            for item in data:
                if cont is None:
                    print(item)
                elif cont in item:
                    print(item)
        else:
            # print count and field
            print("List of " + name + " and total occurrences:")
            for num, item in zip(count, data):
                if cont is None:
                    print(num, item)
                elif cont in item:
                    print(num, item)

    def sort_list(self, data, order):
        """Sort a list of papers"""

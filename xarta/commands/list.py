"""The list command."""

from collections import namedtuple
from .base import Base
from ..database import PaperDatabase

DATA_HEADERS = ("ref", "title", "authors", "category", "tags")
Paper = namedtuple("Paper", DATA_HEADERS)


class List(Base):
    """ List all tags or authors in library. """

    def run(self):
        options = self.options
        obj = options["<obj>"]
        cont = options["--contains"]

        if obj not in {"tags", "authors"}:
            raise ValueError("xarta list only lists tags and authors.")

        paper_database = PaperDatabase()
        tuple_data = paper_database.query_papers(silent=True)
        namedtuple_data = map(lambda x: Paper(*x), tuple_data)

        items = set([])
        for paper in namedtuple_data:
            string_list = getattr(paper, obj)
            list_ = [s.strip() for s in string_list.split(";")]
            for item in list_:
                items.add(item)

        for item in sorted(list(items)):
            if cont is None:
                print(item)
            elif cont in item:
                print(item)

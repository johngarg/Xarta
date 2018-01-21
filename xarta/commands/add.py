"""The open command."""


from json import dumps

from .base import Base
from ..utils import arxiv_open


class Add(Base):
    """Add an arXiv paper and its metadata to the database."""

    def run(self):
        print('Hello, world!')
        options = self.options
        print(options)
        ref = options['<ref>']
        tags = options['--tag']

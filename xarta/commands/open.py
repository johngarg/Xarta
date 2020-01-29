"""The open command."""


from .base import Base
from ..utils import arxiv_open


class Open(Base):
    """Open an arXiv paper with reference"""

    def run(self):
        options = self.options
        ref = options["<ref>"]
        pdf = options["--pdf"]
        arxiv_open(ref, pdf=pdf)

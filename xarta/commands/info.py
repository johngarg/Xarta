"""The info command."""


from json import dumps
import pprint

from .base import Base
from ..utils import get_arxiv_data


class Info(Base):
    """Print all of the information about the paper"""

    def run(self):
        options = self.options
        ref = options['<ref>']
        info = get_arxiv_data(ref)
        pprint.pprint(info)

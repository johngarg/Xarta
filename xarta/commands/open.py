"""The open command."""


from .base import BaseCommand
from ..utils import arxiv_open, process_ref, is_valid_ref, XartaError


class Open(BaseCommand):
    """Open an arXiv paper with reference"""

    def run(self):
        options = self.options
        ref = options["<ref>"]
        pdf = options["--pdf"]

        processed_ref = process_ref(ref)
        if is_valid_ref(processed_ref):
            arxiv_open(processed_ref, pdf=pdf)
        else:
            raise XartaError("Not a valid arXiv reference or alias: " + ref)

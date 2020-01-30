"""The tag editing command."""


from .base import Base
from ..database import PaperDatabase


class Edit(Base):
    """ Edit the tag information in the database for a paper. """

    def run(self):
        options = self.options
        ref = options["<ref>"]
        tags = options["<tags>"]
        action = options["--action"]

        with PaperDatabase() as paper_database:
            paper_database.edit_paper_tags(paper_id=ref, tags=tags, action=action)

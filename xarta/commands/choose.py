"""The choose command."""


from .base import Base
from ..utils import arxiv_open, XartaError
from ..database import PaperDatabase


class Choose(Base):
    """ List papers (by metadata) with an option to open. """

    def run(self):
        options = self.options
        pdf = options["--pdf"]
        ref = options["--ref"]
        filter_ = options["--filter"]
        tag = options["<tag>"]
        author = options["--author"]
        category = options["--category"]
        title = options["--title"]

        with PaperDatabase() as paper_database:
            paper_data = paper_database.query_papers(
                paper_id=ref,
                title=title,
                author=author,
                category=category,
                tags=tag,
                filter_=filter_,
                select=True,
            )

            # how many matching papers are there?
            #
            if len(paper_data) == 0:
                print("No matching papers found!")
                return
            elif len(paper_data) == 1:
                print("Only one match, opening ...")
                choice = 0
            else:
                # more than one choice, get user input
                try:
                    choice = int(input("Paper to open: "))
                except ValueError as err:
                    if "invalid literal for int()" in str(err):
                        raise XartaError("Invalid input, must be integer.")
                    else:
                        raise err
                except KeyboardInterrupt:
                    # KeyboardInterrupt causes an ugly error message when aborting
                    # input. So just catch and exit
                    import sys

                    sys.exit(0)

                # check input
                if not -len(paper_data) <= choice < len(paper_data):
                    raise XartaError("Invalid input, integer out of bounds.")

            # open the paper!
            ref_to_open = paper_data[choice][0]
            arxiv_open(ref_to_open, pdf=pdf)

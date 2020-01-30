"""PaperDatabase class."""

import sqlite3
import os
from . import utils

HOME = os.path.expanduser("~")


def initialise_database(database_path):
    """Initialise database with empty table."""

    print("Creating new database at " + database_path + "...")

    init_command = """
        CREATE TABLE papers
        (id text, title text, authors text, category text, tags text);"""

    conn = sqlite3.connect(database_path)
    with conn:
        print("Initialising database...")
        conn.execute(init_command)

    print("Database initialised!")


def write_database_location(database_path, location_file=HOME + "/.xarta"):
    """Write database location to a file, usually  ~/.xarta """
    with open(location_file, "w") as xarta_file:
        xarta_file.write(database_path)
    print(f"Database location saved to {location_file}")


def read_database_location(location_file):
    """Read database location from a file, usually ~/.xarta, and return path as a string."""
    try:
        with open(location_file, "r") as xarta_file:
            return xarta_file.readline()
    except:
        raise Exception(
            f"Could not read database directory from '{location_file}'. Have you initialised a database?"
        )


class PaperDatabase:
    """The paper database interface."""

    def __init__(self, location_file=HOME + "/.xarta"):
        self.path = read_database_location(location_file=location_file)

    def add_paper(self, paper_id, tags):
        """Add paper to database. paper_id is the arxiv number as a string. The
        tags are a list of strings.
        """
        # clean id
        paper_id = utils.processed_ref(paper_id)

        if not utils.is_valid_ref(paper_id):
            raise Exception(f"Not a valid arXiv reference: {paper_id}")

        if self.contains(paper_id):
            raise Exception("This paper is already in the database.")

        conn = sqlite3.connect(self.path)
        with conn:
            data = utils.get_arxiv_data(paper_id)
            authors = utils.list_to_string(data["authors"])
            # tags = [utils.expand_tag(tag, data) for tag in tags]
            tags = utils.list_to_string(tags)
            title, category = data["title"], data["category"]
            insert_command = f"""
                INSERT INTO papers
                (id, title, authors, category, tags)
                VALUES
                ("{paper_id}", "{title}", "{authors}", "{category}", "{tags}");"""

            conn.execute(insert_command)

        print(f"{paper_id} added to database!")

    def delete_paper(self, paper_id):
        """Remove paper from database."""
        conn = sqlite3.connect(self.path)
        with conn:
            delete_command = f"""DELETE FROM papers WHERE id = "{paper_id}";"""
            conn.execute(delete_command)

        print(f"{paper_id} deleted from database!")

    def get_tags(self, paper_id):
        """Get list of tags for some paper"""
        query_command = f"""SELECT tags FROM papers WHERE id={paper_id};"""

        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute(query_command)
        tags_string = c.fetchall()[0][0]
        return utils.string_to_list(tags_string)

    def edit_paper_tags(self, paper_id, tags, action):
        """Edit paper tags in database."""
        # first: remove duplicates in tags
        tags = list(set(tags))
        conn = sqlite3.connect(self.path)

        with conn:
            if action == "set":
                new_tags = tags
            elif action == "add":
                # add tags to old_tags, but dont add duplicates
                old_tags = self.get_tags(paper_id)
                tags = [tag for tag in tags if tag not in old_tags]
                new_tags = old_tags + tags
            elif action == "delete":
                # remove tags from old_tags
                old_tags = self.get_tags(paper_id)
                new_tags = [tag for tag in old_tags if tag not in tags]
            else:
                raise Exception("Unkown edit action: " + action)

            new_tags = utils.list_to_string(new_tags)
            edit_tags_command = f"""UPDATE papers SET tags = "{new_tags}"
                                    WHERE id = "{paper_id}";"""
            conn.execute(edit_tags_command)

        print(f"{paper_id} now has the following tags in the database: {new_tags}")

    def query_papers(self, silent=False):
        """Query information about a paper in the database."""
        all_rows = utils.get_all_rows_from_db(self.path)

        if not silent:
            from tabulate import tabulate

            # get current console window dimensions
            data = utils.format_data_term(all_rows)

            # prepend arXiv to ref to distinguish from cern doc server papers
            to_be_printed = []
            for row in data:
                new_row = row
                new_row[0] = "arXiv:" + row[0]
                to_be_printed.append(new_row)

            col_names = ["Ref", "Title", "Authors", "Category", "Tags"]
            print(tabulate(to_be_printed, headers=col_names, tablefmt="simple"))

        return all_rows

    def query_papers_contains(
        self,
        paper_id,
        title,
        author,
        category,
        tags,
        filter_,
        silent=False,
        select=False,
    ):
        """Function to search and filter paper database. Returns a list of
        tuples and (if `silent` is False) prints a table to the screen. Search
        parameters connected by a logical OR, thus:

            db.query_papers_contains(paper_id=None, title=None,
                                     author='Weinberg', category='hep-th',
                                     tags=[])

        will return every paper in the database from 'hep-th' as well as those
        by 'Weinberg'.
        """
        library_data = self.query_papers(silent=True)
        data = []
        col_names = ["ref", "title", "authors", "category", "tags"]
        for row in library_data:
            row_dict = dict(zip(col_names, row))
            if paper_id is not None and paper_id in row_dict["ref"]:
                data.append(row)
                continue
            elif title is not None and title in row_dict["title"]:
                data.append(row)
                continue
            elif author is not None and author in row_dict["authors"]:
                data.append(row)
                continue
            elif category is not None and category in row_dict["category"]:
                data.append(row)
                continue
            elif tags is not None and tags != []:
                for tag in tags:
                    if tag in row_dict["tags"]:
                        data.append(row)
                        break  # Don't include same paper twice
                continue
            elif filter_ is not None:
                lambda_prestring = "lambda " + ", ".join(col_names) + ": "
                if eval(lambda_prestring + filter_)(*row_dict.values()):
                    data.append(row)
                    continue

        if not silent:
            from tabulate import tabulate

            short_data = utils.format_data_term(data, select)
            to_be_printed = [["arXiv:" + row[0], *row[1:]] for row in short_data]
            print(
                tabulate(
                    to_be_printed,
                    headers=["Ref", "Title", "Authors", "Category", "Tags"],
                    tablefmt="simple",
                    showindex=(True if select else False),
                )
            )

        return data

    def contains(self, ref):
        """Returns a boolean identifying if an entry with reference `ref`
        exists within the database.
        """
        search_results = self.query_papers_contains(
            paper_id=ref,
            title=None,
            author=None,
            category=None,
            tags=[],
            filter_=None,
            silent=True,
        )
        return bool(search_results)

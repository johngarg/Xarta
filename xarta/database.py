"""PaperDatabase class."""

import sqlite3
import os
from . import utils
from .utils import XartaError, string_to_list, check_filter_is_sanitary


HOME = os.path.expanduser("~")

DATA_HEADERS = ["ref", "title", "authors", "category", "tags", "alias"]


def initialise_database(database_location, config_file=HOME + "/.xarta"):
    """Initialise database with empty table and update file that points to database.
    If database already exists, just update the file"""

    # resolve relative paths, e.g., 'xarta init ./'
    database_location = os.path.abspath(database_location)

    # verify folder exists
    if not os.path.isdir(database_location):
        raise XartaError("Directory does not exist.")

    # create xarta directory
    database_location += "/.xarta.d"
    os.makedirs(database_location, exist_ok=True)
    database_path = database_location + "/db.sqlite3"

    # check if file already exists
    if "db.sqlite3" not in os.listdir(database_location):

        print("Creating new database at " + database_path + "...")

        init_command = 'CREATE TABLE papers (id text UNIQUE, title text, authors text, category text, tags text, alias text DEFAULT "" );'

        with sqlite3.connect(database_path) as connection:
            print("Initialising database...")
            connection.execute(init_command)
        connection.close()

        print("Database initialised!")
    else:

        print(database_path + " already exists.")

    write_database_path(database_path, config_file=config_file)


def write_database_path(database_path, config_file):
    """Write database location to a file, usually  ~/.xarta """
    with open(config_file, "w") as xarta_file:
        xarta_file.write(database_path)
    print(f"Database location saved to {config_file}")


def read_database_path(config_file):
    """Read database location from a file, usually ~/.xarta, and return path as a string."""
    try:
        with open(config_file, "r") as xarta_file:
            return xarta_file.readline()
    except:
        raise XartaError(
            f"Could not read database directory from '{config_file}'. Have you initialised a database?"
        )


class PaperDatabase:
    """The paper database interface."""

    def __init__(self, path=None, config_file=HOME + "/.xarta"):
        self.config_file = config_file
        self.path = path
        self.connection = None
        self.cursor = None

    def __enter__(self):
        if self.path is None:
            self.path = read_database_path(self.config_file)
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        self.check_database_version()
        return self

    def __exit__(self, error_type, value, traceback):
        if traceback is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()

    def check_database_version(self):
        """Check version of database. If database was created using an older version of
        xarta, insert new rows"""
        self.cursor.execute("PRAGMA table_info(papers)")
        columns = self.cursor.fetchall()
        if len(columns) == 5:
            # v1 database. Is missing the alias column!
            print("Updating database file.")
            self.cursor.execute('ALTER TABLE papers ADD alias text DEFAULT "" ')

    def get_all_aliases(self):
        """get a list of all aliases."""
        self.cursor.execute("SELECT alias FROM papers")
        results = self.cursor.fetchall()
        aliases = [row[0] for row in results]
        return aliases

    def resolve_alias(self, alias):
        """Find the paper_id associated with an alias. Return False if the alias does
        not exist"""
        self.cursor.execute("SELECT id FROM papers WHERE alias=?", (alias,))
        results = self.cursor.fetchall()
        if not results:
            return ""
        return results[0][0]

    def add_paper(self, paper_id, tags, alias):
        """Add paper to database. paper_id is the arxiv number as a string. The
        tags are a list of strings.
        """
        if alias and alias in self.get_all_aliases():
            raise XartaError("Alias is not unique!")

        if self.contains(paper_id):
            raise XartaError("This paper is already in the database.")

        data = utils.get_arxiv_data(paper_id)
        authors = utils.list_to_string(data["authors"])
        # tags = [utils.expand_tag(tag, data) for tag in tags]
        tags = utils.list_to_string(tags)
        title, category = data["title"], data["category"]
        insert_command = "INSERT INTO papers (id, title, authors, category, tags, alias) VALUES (?, ?, ?, ?, ?, ?);"

        self.cursor.execute(
            insert_command, (paper_id, title, authors, category, tags, alias)
        )

        print(f"{paper_id} added to database!")

    def delete_paper(self, paper_id):
        """Remove paper from database."""
        self.cursor.execute("DELETE FROM papers WHERE id = ?;", (paper_id,))

        print(f"{paper_id} deleted from database!")

    def get_tags(self, paper_id):
        """Get list of tags for some paper"""
        self.cursor.execute("SELECT tags FROM papers WHERE id=?;", (paper_id,))
        tags_string = self.cursor.fetchall()[0][0]
        return utils.string_to_list(tags_string)

    def set_paper_alias(self, paper_id, alias):
        """Edit the alias of a paper in the database."""

        self.cursor.execute(
            "UPDATE papers SET alias = ? WHERE id = ?;", (alias, paper_id),
        )
        if alias:
            print(f"{paper_id} is now aliased to: {alias}")
        else:
            print(f"Removed alias from {paper_id}")

    def rename_tag(self, old_tag, new_tag=None):
        """Rename or remove a tag from every paper"""

        matching_papers = self.query_papers(
            None, None, None, None, [old_tag], None, silent=True, exact_tags=True
        )
        for paper in matching_papers:
            self.edit_paper_tags(
                paper_id=paper[0], tags=[old_tag], action="delete", silent=True,
            )
            if new_tag is not None:
                self.edit_paper_tags(
                    paper_id=paper[0], tags=[new_tag], action="add", silent=True,
                )

        if new_tag is None:
            print(f"All instances of the tag '{old_tag}' were removed")
        else:
            print(
                f"All instances of the tag '{old_tag}' were replaced with '{new_tag}'"
            )

    def edit_paper_tags(self, paper_id, tags, action, silent=False):
        """Edit paper tags in database."""
        # first: remove duplicates in tags
        tags = list(set(tags))

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
            raise XartaError("Unkown edit action: " + action)

        new_tags = utils.list_to_string(new_tags)
        self.cursor.execute(
            f"""UPDATE papers SET tags = ?
                                WHERE id = ?;""",
            (new_tags, paper_id),
        )

        if not silent:
            print(f"{paper_id} now has the following tags in the database: {new_tags}")

    def get_all_papers(self):
        """Get all papers"""
        query_command = f"""SELECT * FROM papers;"""
        self.cursor.execute(query_command)
        return self.cursor.fetchall()

    def print_all_papers(self, select=False):
        """Print a table of all the papers"""
        data = self.get_all_papers()
        self.print_papers(data, select=select)
        if select:
            return data

    def query_papers(
        self,
        paper_id,
        title,
        author,
        category,
        tags,
        filter_,
        silent=False,
        select=False,
        exact_tags=False,
        error_on_empty=True,
    ):
        """Function to search and filter paper database. Returns a list of
        tuples and (if `silent` is False) prints a table to the screen. Search
        parameters connected by a logical OR, thus:

            db.query_papers_contains(paper_id=None, title=None,
                                     author='Weinberg', category='hep-th',
                                     tags=[])

        will return every paper in the database from 'hep-th' as well as those
        by 'Weinberg'. The exact_tags option determines how tag-matching is
        done. If exact_tags=False, then a search for quarks will return both
        papers tagged as quarks and leptoquarks.
        """

        if filter_ is not None:
            # check if the provided filter is sanitary/safe.
            # throws errors with helpfull messages if not sanitary
            check_filter_is_sanitary(filter_, DATA_HEADERS)

        library_data = self.get_all_papers()
        data = []
        for row in library_data:
            row_dict = dict(zip(DATA_HEADERS, row))
            if exact_tags:
                # tags are currently a long, comma separated, string. using the
                # "in" keyword searches the string. By converting it to a list of
                # tags, the 'in' keyword will match only complete tags in the
                # list.
                row_dict["tags"] = string_to_list(row_dict["tags"])

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
                try:
                    # use a dict to define accesibe variables in the eval: even though
                    # variable names should not be capitalised, users may try and write
                    # the variables as they appear in the table header (capitalised). so
                    # I am including capitalised variables
                    eval_vars = {"__builtins__": {}}
                    eval_vars.update(row_dict)
                    for k in DATA_HEADERS:
                        eval_vars[k.capitalize()] = eval_vars[k]
                    # evaliate filter!
                    if eval(filter_, eval_vars):
                        data.append(row)
                        continue
                except Exception:
                    raise XartaError("Error when evaluating filter.")

        if not data:
            raise XartaError("No matching papers found!")

        if not silent:
            self.print_papers(data, select)

        return data

    def contains(self, ref):
        """Returns a boolean identifying if an entry with reference `ref`
        exists within the database.
        """
        self.cursor.execute("SELECT 1 FROM papers WHERE id = ?;", (ref,))
        return bool(self.cursor.fetchall())

    def assert_contains(self, ref):
        """Returns a boolean identifying if an entry with reference `ref`
        exists within the database. If not, raise an error."""
        if not self.contains(ref):
            raise XartaError(f"Reference does not exist in database: {ref}")

    def print_papers(self, data, select):

        from tabulate import tabulate

        # process data for printing (fit to screen)
        formated_data = utils.format_data_term(data, select)

        # capitalise headers
        headers = [head.capitalize() for head in DATA_HEADERS]

        # print!
        print(
            tabulate(
                formated_data, headers=headers, tablefmt="simple", showindex=select,
            )
        )

import sqlite3
import os
from .utils import get_arxiv_data, list_to_string, expand_tag, format_data_term

HOME = os.path.expanduser('~')

class PaperDatabase():
    def __init__(self, path):
        self.path = path

    def create_connection(self):
        """ Create a database connection to a SQLite database. """
        print('Creating new database at ' + self.path + '...')
        conn = sqlite3.connect(self.path)
        conn.close()
        with open(HOME+'/.xarta', 'w') as xarta_file:
            xarta_file.write(self.path)

    def initialise_database(self):
        """ Initialise database with empty table. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        print('Initialising database...')
        c.execute('''CREATE TABLE papers (id text, title text, authors text, category text, tags text);''')
        conn.commit()
        conn.close()
        print('Database initialised!')

    def add_paper(self, paper_id, tags):
        """Add paper to database. paper_id is the arxiv number as a string. The tags
        are a list of strings.
        """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = get_arxiv_data(paper_id)
        author_string = list_to_string(data['authors'])
        tags = [expand_tag(tag, data) for tag in tags]
        tags = list_to_string(tags)

        insert_command = f'''INSERT INTO papers (id, title, authors, category, tags) VALUES ("{paper_id}", "{data['title']}", "{author_string}", "{data['category']}", "{tags}");'''
        c.execute(insert_command)
        print(f"{paper_id} added to database!")
        conn.commit()
        conn.close()

    # currently unused
    def add_local_paper(self, paper_id, tags, path, title='', authors=[]):
        """ Add paper to database. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = {'title': title, 'authors': authors, 'category': 'local'}
        author_string = list_to_string(data['authors'])
        tags = [expand_tag(tag, data) for tag in tags]
        tags = list_to_string(tags)

        insert_command = f'''INSERT INTO papers (id, title, authors, category, tags) VALUES ("{paper_id}", "{data['title']}", "{author_string}", "{data['category']}", "{tags}");'''
        c.execute(insert_command)
        print(f"{paper_id} added to database from {path}!")
        conn.commit()
        conn.close()


    def delete_paper(self, paper_id):
        """ Remove paper from database. """

        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        data = get_arxiv_data(paper_id)
        delete_command = f'''DELETE FROM papers WHERE id = "{paper_id}";'''
        c.execute(delete_command)
        print(f"{paper_id} deleted from database!")
        conn.commit()
        conn.close()

    def edit_paper_tags(self, paper_id, new_tags):
        """ Edit paper tags in database. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        new_tags = list_to_string(new_tags)

        edit_tags_command = f'''UPDATE papers SET tags = "{new_tags}" WHERE id = "{paper_id}";'''
        c.execute(edit_tags_command)
        print(f"{paper_id} now has the following tags in the database: {new_tags}")
        conn.commit()
        conn.close()

    def query_papers(self, silent=False):
        """ Query information about a paper in the database. """
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        query_command = f'''SELECT * FROM papers;'''
        query_results = c.execute(query_command)
        all_rows = c.fetchall()

        # get current console window dimensions
        data = format_data_term(all_rows)
        if not silent:
            from tabulate import tabulate
            to_be_printed = [['arXiv:'+row[0], *row[1:]] for row in data]
            print(
                tabulate(to_be_printed,
                         headers=['Ref', 'Title', 'Authors', 'Category', 'Tags'],
                         tablefmt="simple"))
        conn.close()
        return all_rows

    def query_papers_contains(self, paper_id, title, author, category, tags, filter,
                              silent=False, select=False):
        """
        Function to search and filter paper database. Returns a list of
        tuples and (if `silent` is False) prints a table to the screen. Search
        parameters connected by a logical OR, thus:
           db.query_papers_contains(paper_id=None,
                                    title=None,
                                    author='Weinberg',
                                    category='hep-th',
                                    tags=[])
        will return every paper in the database from 'hep-th' as well as those
        by 'Weinberg'.
        """
        library_data = self.query_papers(silent=True)
        data = []
        lambda_prestring = 'lambda ref, title, authors, category, tags: '
        for row in library_data:
            row_dict = dict(zip(['ref', 'title', 'authors', 'category', 'tags'], row))
            if paper_id is not None and paper_id in row_dict['ref']:
                data.append(row)
                continue
            elif title is not None and title in row_dict['title']:
                data.append(row)
                continue
            elif author is not None and author in row_dict['authors']:
                data.append(row)
                continue
            elif category is not None and category in row_dict['category']:
                data.append(row)
                continue
            elif tags is not None and tags != []:
                for tag in tags:
                    if tag in row_dict['tags']:
                        data.append(row)
                        break # Don't include same paper twice
                continue
            elif filter is not None:
                if eval(lambda_prestring+filter)(*row_dict.values()):
                    data.append(row)
                    continue

        if not silent:
            from tabulate import tabulate
            short_data = format_data_term(data)
            to_be_printed = [['arXiv:'+row[0], *row[1:]] for row in short_data]
            print(
                tabulate(to_be_printed,
                         headers=['Ref', 'Title', 'Authors', 'Category', 'Tags'],
                         tablefmt="simple",
                         showindex=(True if select else False)))

        return data

    def contains(self, ref):
        """
        Returns a boolean identifying if an entry with reference `ref` exists
        within the database.
        """
        search_results = self.query_papers_contains(
            paper_id=ref,
            title=None,
            author=None,
            category=None,
            tags=[],
            filter=None,
            silent=True)
        return bool(search_results)

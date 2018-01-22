import sqlite3
import os

HOME = os.path.expanduser('~')

def create_connection(database):
    """ Create a database connection to a SQLite database. """
    print('Creating new database at ' + database + '...')
    conn = sqlite3.connect(database)
    conn.close()
    with open(HOME+'/.xarta', 'w') as xarta_file:
        xarta_file.write(database)

def initialise_database(database):
    """ Initialise database with empty table. """
    conn = sqlite3.connect(database)
    c = conn.cursor()
    print('Initialising database...')
    c.execute('''CREATE TABLE papers
                 (id text, title text, abstract text, authors text, category text)''')
    conn.commit()
    conn.close()
    print('Database initialised!')

import sqlite3
import os

DATABASE_DIR = '/Users/johngargalionis/Dropbox/.xarta.d/'
DATABASE = 'db.sqlite'
DATABASE_PATH = DATABASE_DIR + DATABASE

def create_connection(database):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(database)
        print('Creating new database at ' + database)
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()

if DATABASE not in os.listdir(DATABASE_DIR):
    print(DATABASE_PATH+' not found...')
    create_connection(DATABASE_PATH)

# conn = sqlite3.connect(DATABASE)
# c = conn.cursor()

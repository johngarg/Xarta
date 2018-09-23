from urllib.request import urlopen
import json
import requests
import os
import xmltodict
from sys import platform

if platform.startswith('linux'):
    open_command = 'xdg-open '
elif platform.startswith('darwin'):
    open_command = 'open '
else:
    raise ValueError('Xarta is currently not supported on Windows.')

# set of arxiv categories only used for opening the "new" page of results from
# the command line
ARXIV_CATEGORIES = {
    'astro-ph', 'cond-mat', 'gr-qc', 'hep-ex', 'hep-lat', 'hep-ph', 'hep-th',
    'math-ph', 'nlin', 'nucl-ex', 'nucl-th', 'physics', 'quant-ph', 'math',
    'CoRR', 'q-bio', 'stat', 'eess', 'econ'
}

def is_arxiv_category(s):
    return s in ARXIV_CATEGORIES

# TODO This is currently not very precise but does the job.
def is_arxiv_ref(s):
    """ Returns True if s is a valid arXiv reference. """
    x = s.split('.')
    return (len(x) == 2 and len(x[0]) == 4) or (len(x[0].split('/')) == 2)

def arxiv_open(ref, pdf=False):
    if is_arxiv_category(ref):
        os.system(open_command + ' https://arxiv.org/list/' + ref + '/new')
    elif is_arxiv_ref(ref):
        if pdf:
            os.system(open_command + ' https://arxiv.org/pdf/' + ref + '.pdf')
        else:
            os.system(open_command + ' https://arxiv.org/abs/' + ref)
    else:
        raise ValueError('`xarta open` received an invalid <ref>.')
    return None

def get_arxiv_data(ref):
    """ Returns a dictionary of data about the reference `ref`. """
    url = 'http://export.arxiv.org/api/query?id_list=' + ref
    xml_data = urlopen(url).read().decode('utf-8')
    data = xmltodict.parse(xml_data)['feed']['entry']
    string_format = lambda s: s.replace('\r', '').replace('\n', '').replace('  ', ' ')
    authors = [auth['name'] for auth in data['author']] \
              if isinstance(data['author'], list) else [data['author']['name']]
    dic = {'id': data['id'],
           'title': string_format(data['title']),
           'authors': authors,
           'category': data['arxiv:primary_category']['@term']}
    return dic

def list_to_string(lst):
    """
    Takes a list of items (strings) and returns a string of items separated by
    semicolons.
    e.g.
        list_to_string(['John', 'Alice'])
            #=> 'John; Alice'
    """
    return '; '.join(lst)

def expand_tag(tag, dic):
    if tag[0] == '#':
        return dic[tag[1:]]
    else:
        return tag

def read_xarta_file():
    """
    Read database location from ~/.xarta file and returns path as string.
    """
    HOME = os.path.expanduser('~')
    try:
        with open(HOME+'/.xarta', 'r') as xarta_file:
            return xarta_file.readline()
    except:
        raise Exception(f'Could not read {HOME}/.xarta')

def format_data_term(data):
    term_rows, term_columns = os.popen('stty size', 'r').read().split()
    l = (int(term_columns) // 5) - 1 # max chars in col
    short_data = [[(c if len(c) < l else c[:(l-3)] + "...")
                   for c in row]
                  for row in data]
    return short_data

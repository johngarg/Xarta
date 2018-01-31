from urllib.request import urlopen
import json
import requests
import os
import xmltodict

open_command = 'open ' # TODO make more general, will only work on mac and with default browser
ARXIV_CATEGORIES = {'hep-ph', 'hep-th', 'hep-ex'} # add whatever you like here...

def is_arxiv_category(s):
    return s in ARXIV_CATEGORIES

def is_arxiv_ref(s):
    """ Returns True if s is a valid arXiv reference. """
    # TODO Fill this out more...
    x = s.split('.')
    return len(x[0]) == 4

def arxiv_open(ref, pdf=False):
    if is_arxiv_category(ref):
        os.system(open_command + ' https://arxiv.org/list/'+ref+'/new')
    elif is_arxiv_ref(ref):
        if pdf:
            os.system(open_command + ' https://arxiv.org/pdf/'+ref+'.pdf')
        else:
            os.system(open_command + ' https://arxiv.org/abs/'+ref)
    else:
        raise ValueError('`xarta open` received an invalid <ref>.')
    # data = get_arxiv_data(ref)
    # msg = "Opening '" + data['title'] + "'"
    # if pdf:
    #     link = data['links']
    #     msg += ' [pdf]'
    # else:
    #     link = data['id']
    # os.system(open_command + link)
    # print(msg)
    return None

def get_arxiv_data(ref):
    url = 'http://export.arxiv.org/api/query?search_query=all:'+ref+'&start=0&max_results=1'
    xml_data = urlopen(url).read().decode('utf-8')
    data = xmltodict.parse(xml_data)['feed']['entry']
    string_format = lambda s: s.replace('\r', '').replace('\n', '').replace('  ', ' ')
    authors = [auth['name'] for auth in data['author']] if isinstance(data['author'], list) else [data['author']['name']]
    dic = {'id': data['id'],
           # 'links': [link['@href'] for link in data['link']],
           'title': string_format(data['title']),
           'abstract': data['summary'],
           'authors': authors,
           'comments': data['arxiv:comment']['#text'],
           'category': data['arxiv:primary_category']['@term']}
    return dic

def list_to_string(lst):
    """
    Takes a list of items (strings) and returns a string of items separated by semicolons.
    e.g.
        list_to_string(['John', 'Alice'])
            #=> 'John; Alice'
    """
    lst_string = ''
    for item in lst:
        lst_string += item + '; '
    return lst_string[:-2]

def expand_tag(tag, dic):
    if tag[0] == '#':
        return dic[tag[1:]]
    else:
        return tag

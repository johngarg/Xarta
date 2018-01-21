from urllib.request import urlopen
import json
import requests
import os
import xmltodict

TEST_REF = '1801.05805'
open_command = 'open '

def arxiv_open(ref, pdf=False):
    data = get_arxiv_data(ref)
    msg = "Opening '" + data['title'] + "'"
    if pdf:
        link = data['pdflink']
        msg += ' [pdf]'
    else:
        link = data['link']
    os.system(open_command + link)
    print(msg)
    return None

def get_arxiv_data(ref):
    url = 'http://export.arxiv.org/api/query?search_query=all:'+ref+'&start=0&max_results=1'
    xml_data = urlopen(url).read().decode('utf-8')
    data = xmltodict.parse(xml_data)['feed']['entry']
    dic = {'link': data['link'][0]['@href'],
           'pdflink': data['link'][1]['@href'],
           'title': data['title'],
           'abstract': data['summary'],
           'authors': [auth['name'] for auth in data['author']],
           'comments': data['arxiv:comment']['#text'],
           'categories': [cat['@term'] for cat in data['category']]}
    return dic

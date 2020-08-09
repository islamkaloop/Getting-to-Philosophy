import sys
import requests
import urllib.parse 
import lxml.html as lh
import time

if len(sys.argv) != 2:
    print("python wiki_Philosophy.py 'URL'")
    sys.exit()

BASE_URL = sys.argv[1]
end = "Philosophy"

def valid_page(page):   
    SPACES = ['File:',
                'File talk:',
                'Wikipedia:',
                'Wikipedia talk:',
                'Project:',
                'Project talk:',
                'Portal:',
                'Portal talk:',
                'Special:',
                'Help:',
                'Help talk:',
                'Template:',
                'Template talk:',
                'Talk:',
                'Category:',
                'Category talk:']
    out = True
    for space in SPACES:
        if(page.startswith(space)):
            out = False
            break
    return out

def strip_parentheses(string):

    nested_parentheses = nesting_level = 0
    result = ''
    for c in string:
        if nested_parentheses < 1:
            if c == '<':
                nesting_level += 1
            if c == '>':
                nesting_level -= 1

        if nesting_level < 1:
            if c == '(':
                nested_parentheses += 1
            if nested_parentheses < 1:
                result += c
            if c == ')':
                nested_parentheses -= 1

        else:
            result += c

    return result

visited = []
def recurse(url):
    print("> " + url)
    page = url[len('https://en.wikipedia.org/wiki/'):]
    if(page in visited): 
        del visited[:]
        print("\n> Loop!")
        return
    if(page == end): 
        del visited[:]
        print("\n> get "+end)
        return
    visited.append(page)
    url += "?action=render"
    result = requests.get(url)
    html = lh.fromstring(result.text)
    for elm in html.cssselect('.reference,span,div,.thumb,table,a.new,i,#coordinates'):
            elm.drop_tree()
    html = lh.fromstring(strip_parentheses(lh.tostring(html).decode('utf-8')))
    next_page = None
    link_found = False
    for _, attr, link, _ in html.iterlinks():
        if(attr != "href"):
            continue
        next_page = link

        if not next_page.startswith('//en.wikipedia.org/wiki/'):
            continue
        next_page = next_page[len('//en.wikipedia.org/wiki/'):]
        next_page = urllib.parse.unquote(next_page)
        if not valid_page(next_page):
                continue
        link_found = True
        break
    if(next_page != None and link_found):
        time.sleep(0.5)
        recurse('https://en.wikipedia.org/wiki/'+next_page)
    else:
        del visited[:]
        print("\n> We are in an article without any outgoing Wikilinks")

recurse(BASE_URL)
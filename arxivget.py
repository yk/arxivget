#!/usr/bin/env python3

import feedparser
import os
import requests
import string
import time

VALID_CHARS = "-_().: %s%s" % (string.ascii_letters, string.digits)


def main():
    # time.sleep(10)
    try:
        requests.get("http://www.google.com")
    except:
        print("no internet connection")
        exit(0)
    config_fn = os.path.expanduser('~/.arxivgetrc')
    with open(config_fn) as f:
        for line in f:
            if line.startswith('lists'):
                lists = line.strip().split('=')[1].strip().split(',')
            if line.startswith('directory'):
                directory = os.path.expanduser(line.strip().split('=')[1].strip())
            if line.startswith('numpapers'):
                numpapers = int(line.strip().split('=')[1].strip())
    if not os.path.exists(directory):
        os.makedirs(directory)
    db = []
    db_fn = os.path.join(directory, 'db.txt')
    if os.path.exists(db_fn):
        with open(db_fn) as f:
            db = set(l.strip() for l in f.readlines() if len(l.strip()) > 0)
    for l in lists:
        print("checking", l)
        page = requests.get('http://export.arxiv.org/api/query?search_query=cat:{}&start=0&max_results={}&sortBy=lastUpdatedDate&sortOrder=descending'.format(l, numpapers))
        feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
        feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
        feed = feedparser.parse(page.content)
        for entry in feed.entries:
            eid, etitle, edate = entry.id, entry.title, entry.updated
            aid = eid.split('/')[-1]
            if aid not in db:
                efn = '{} {}.pdf'.format(edate, ''.join(c for c in etitle.replace('  ', ' ') if c in VALID_CHARS))
                pdf_url = eid.replace('/abs/', '/pdf/')
                pdf_dir = os.path.join(directory, l)
                if not os.path.exists(pdf_dir):
                    os.makedirs(pdf_dir)
                pdf_fn = os.path.join(pdf_dir, efn)
                print('downloading', pdf_url)
                pdf = requests.get(pdf_url).content
                with open(pdf_fn, 'wb') as f:
                    f.write(pdf)
                    db.add(aid)

    with open(db_fn, 'w') as f:
        f.writelines(['{}\n'.format(l) for l in db])


if __name__ == '__main__':
    main()

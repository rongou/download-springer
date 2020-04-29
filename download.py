#!/usr/bin/env python3

import argparse
import csv
import datetime
import os
import shutil
import urllib.request

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/81.0.4044.129 Safari/537.36 '


def read_tsv(tsv_file):
    with open(tsv_file) as f:
        reader = csv.DictReader(f, delimiter='\t')
        return list(reader)


def same_book(one, two):
    return (one['Book Title'] == two['Book Title'] and
            one['Author'] == two['Author'] and
            one['Edition'] == two['Edition'])


def get_part(prev_part, rows, i):
    part = ''
    if prev_part == '':
        if i < len(rows) - 1 and same_book(rows[i], rows[i + 1]):
            part = 'A'
    elif same_book(rows[i - 1], rows[i]):
        part = chr(ord(prev_part) + 1)
    return part


def download_file(doi, output_file):
    url = f'https://link.springer.com/content/pdf/{doi}.pdf'
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request) as response:
        with open(output_file, 'wb') as o:
            shutil.copyfileobj(response, o)


def download(tsv_file, output_dir):
    rows = read_tsv(tsv_file)

    part = ''
    for i, row in enumerate(rows):
        title = row['Book Title'].replace('/', '-').replace(':', '-')
        author = row['Author']
        edition = row['Edition']

        part = get_part(part, rows, i)
        if part == '':
            filename = f"{title} - {author} - {edition}.pdf"
        else:
            filename = f"{title} (Part {part}) - {author} - {edition}.pdf"

        output_file = os.path.join(output_dir, filename)
        if os.path.exists(output_file):
            print(f'{datetime.datetime.now()} Skipping {filename}')
        else:
            print(f'{datetime.datetime.now()} Downloading {filename}')
            doi = row['DOI URL'][15:].replace('/', '%2F')
            download_file(doi, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tsv_file")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    download(args.tsv_file, args.output_dir)


if __name__ == "__main__":
    main()

import pdfx
import pdfx.exceptions
import click
import sys
import os
from urllib.request import urlretrieve, URLError
from multiprocessing import Pool
from functools import partial
from typing import List
import re


def get_url_from_pdf(pdf_text: str) -> List[str]:
    """Processes a raw text representation of a pdf to get the url out.
    
    :param pdf_text: A pdfx converted text version of the pdf
    :return: A list of the urls
    """
    url_pat = r'([a-zA-Z0-9\/\.\-\_]*)'
    url_regex_string = r'(http\:\/\/)' + url_pat + r'(\n)' + url_pat
    url_regex = re.compile(url_regex_string)
    res = url_regex.findall(pdf_text)
    urls = [''.join((a[0], a[1], a[3])) for a in res]
    return urls


def download(url: str, dest: str) -> bool:
    try:
        local_name, headers = urlretrieve(url)
    except URLError:
        return False
    else:
        filename = url.split('/')[-1]
        os.renames(local_name, os.path.join(os.getcwd(), dest, filename))
        return True


def download_urls(urls: List, dest: str) -> bool:
    function = partial(download, dest=dest)
    p = Pool(len(urls))
    p.map(function, urls)
    return True
    # for url in urls:
    #     function(url)


@click.command()
@click.argument('filename')
@click.option('--outdir', default='output')
def main(filename, outdir):
    """"""
    try:
        pdf_extractor = pdfx.PDFx(uri=filename)
    except pdfx.exceptions.FileNotFoundError:
        print("File not found: {}".format(filename), file=sys.stderr)
    else:
        pdf_text = pdf_extractor.get_text()
        urls = get_url_from_pdf(pdf_text=pdf_text)
        download_urls(urls, dest=outdir)

if __name__ == '__main__':
    main()
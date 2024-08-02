#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace
import logging
import os
import re

from bs4 import BeautifulSoup
import requests

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

BASE_URL = 'https://ftp.ebi.ac.uk/pub/databases/merops/current_release/seqlib/'


def main(args: Namespace) -> None:
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
    
    response = requests.get(BASE_URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        for filename in filter(lambda link: re.match(r'^[a-z]\d+\.lib$', link),
                               map(lambda a: a['href'], soup.find_all('a'))):
            response = requests.get(BASE_URL + filename)

            if response.status_code == 200:
                with open(args.outdir + filename, 'wb') as file:
                    file.write(response.content)
                
                logging.info(f'File {filename} was successfully downloaded')
            else:
                logging.warning(f'Failed to download {filename}. '
                                f'Status code: {response.status_code}')
    else:
        logging.error(f'Failed to download MEROPS data. '
                      f'Status code: {response.status_code}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--outdir', '-o', default='./merops/')
    main(parser.parse_args())

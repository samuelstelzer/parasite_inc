from datetime import datetime
from chardet import detect
import re
import logging
import argparse

import pandas as pd
from pandas import read_csv

from tkinter import Tk
from tkinter.filedialog import askopenfilename


parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', action='store_true', help='Show debug info.')
parser.add_argument('--filepath', '-f', help='Filepath of csv file. If not given select dialogue is triggered.', default=False)

logger = logging.getLogger()


def format(text: str, plain: bool =False):
    bold = '\033[1m'
    red = '\033[1;31m'
    green = '\033[1;32m'
    reset = '\033[0m'

    if plain:
        return text.replace('$BOLD', '').replace('$RED', '').replace('$GREEN', '').replace('$RESET', '')
    else:
        return text.replace('$BOLD', bold).replace('$RED', red).replace('$GREEN', green).replace('$RESET', reset)


def main(srcfile):

    if not srcfile:
        Tk().withdraw()
        srcfile = askopenfilename()
    if not srcfile.endswith('.csv'):
        logger.error('\033[1;31mProvide a csv file!\033[0m')
        return

    trgfile = srcfile.replace('.csv', '_fixed.xlsx')

    logger.debug(f'Trying to convert source csv file to encoding \'utf-8\'...')
    with open(srcfile, 'rb') as f:
        rawdata = f.read()
    from_codec = detect(rawdata)['encoding']
    logger.debug(f'Source encoding \'{from_codec}\' detected...')
    try:
        logger.debug(f'Converting source csv file from \'{from_codec}\' to \'utf-8\'...')
        with open(srcfile, 'r', encoding=from_codec) as f, open(trgfile, 'w', encoding='utf-8') as e:
            text = f.read()
            e.write(text)
    except UnicodeDecodeError as e:
        logger.error('Decode Error')
        raise e
    except UnicodeEncodeError as e:
        logger.error('Encode Error')
        raise e

    lines = []
    logger.debug(f'Fixing csv file...')
    with open(trgfile) as f:
        for i, raw_line in enumerate(f.readlines()):
            line = re.sub(r'^"|"$', '', raw_line)
            line = re.sub(r'"+', '"', line)
            line = re.sub(r'\'', '\'', line)
            if line != raw_line:
                logger.debug(f'Fixed line {i}.')
            lines.append(line)

    logger.debug(f'Saving fixed in csv file as \'{trgfile}\'...')
    with open(trgfile, 'w') as f:
        f.writelines(lines)
    logger.debug(f'Reading fixed in csv file...')
    sales = read_csv(trgfile)

    logger.debug(f'Adding tax percentage...')
    sales['date'] = pd.to_datetime(sales.date)
    sales['reduced tax'] = sales['date'].ge(datetime(2020, 7, 1)) & sales['date'].le(datetime(2020, 12, 31))
    sales['tax percentage'] = .19
    sales.loc[sales['reduced tax'], 'tax percentage'] = .16

    xlsx_file = trgfile.replace('.csv', '.xlsx')
    logger.debug(f'Saving in excel file \'{xlsx_file}\'...')
    sales.to_excel(xlsx_file, index=False)

    logger.debug(f'Calculating totals...')
    total_amount = sales['amount you received'].sum()
    total_tax = (sales['amount you received'] * sales['tax percentage']).sum()
    min_date = sales['date'].min().strftime('%Y/%m/%d')
    max_date = sales['date'].max().strftime('%Y/%m/%d')
    res = f'total gross: $BOLD{total_amount:.2f}$RESET\n' \
          f'total net: $GREEN{total_amount - total_tax:.2f}$RESET\n' \
          f'total tax: $RED{total_tax:.2f}$RESET\n' \
          f'avg. tax percentage: {total_tax / total_amount:.0%}\n' \
          f'evaluated range: {min_date} - {max_date}'

    logger.info(format(res))

    with open(srcfile.replace('.csv', '_result.txt'), 'w') as f:
        f.write(format(res, True))


if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=logging.DEBUG if args.debug else logging.INFO)
    try:
        main(args.filepath)
    except Exception as e:
        logger.error('\033[1;31mSomething went wrong. Please call customer support.\033[0m')

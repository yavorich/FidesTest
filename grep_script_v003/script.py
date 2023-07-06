import argparse
from pprint import pprint
import logging
import sys
import os
import csv
import re

from utils import read_config

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(message)s')

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-i', '--input_file', required=True, help='input file')
parser.add_argument('-o', '--output_file', required=True, help='output file')
parser.add_argument('-s', '--search_config', required=True, help='seacrh config ini file')
parser.add_argument('-c', '--config', default=os.path.join(SCRIPT_DIR, 'config.ini'), help='config file')
parser.add_argument('-w', '--weights', required=True, help='words/suffixes weights file')
parser.add_argument('-b', '--begin', help='start with specific input line')
parser.add_argument('-p', '--progress_file', default=os.path.join(SCRIPT_DIR, '.last_success_md5.tmp.txt'), help='file for last succeffsully finsihed md5 record')

args = parser.parse_args()

logging.info('Parsing args')

input_file = args.input_file
output_file = args.output_file
search_config = args.search_config
config = args.config
filepath_weights_csv = args.weights
begin = args.begin
progress_file = args.progress_file

logging.info('Command line args (including defaults):')
logging.info(args)

logging.info('Check if input file exists (expected: true)')
if not os.path.exists(input_file):
    raise Exception(f'Input file doesn\'t exists ({input_file})')

logging.info('Check if output file exists (expected: false)')
if not os.path.exists(output_file):
    logging.warning(f'WARNING Output file exists - will be overwriten')

logging.info('Parsing general config')
config = read_config(config)

separator = config.get('Input', 'separator')
columns = [*map(lambda column: column.strip(), config.get('Input', 'columns').split(','))]
index_column = config.get('Input', 'index_column')

logging.info(f'Separator: {separator}; Columns: {columns}; Index column: {index_column}')

logging.info('Parsing search config')
search_config = read_config(search_config)

suffix_max_padding = int(search_config.get('SearchFor', 'suffix_max_padding'))
column_to_search = search_config.get('SearchFor', 'column_to_search')
search_mode = search_config.get('SearchFor', 'search_mode')

logging.info(f'suffix_max_padding: {suffix_max_padding}; column_to_search: {column_to_search}; search_mode: {search_mode}')

suffixes_w_weights = {}
words_w_weights = {}

with open(filepath_weights_csv) as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        selector = row[0].lower()
        weight = row[1]
        is_word = row[2] == '1'
        if is_word:
            words_w_weights[selector] = int(weight)
        else:
            suffixes_w_weights[selector] = int(weight)
        print(selector, weight, is_word)

logging.info(f'Words: {words_w_weights}')
logging.info(f'Suffixes: {suffixes_w_weights}')

logging.info('Suffixes weights:')
logging.info(suffixes_w_weights)

logging.info('READY')

begin_reached = False

with open(input_file) as f:
    lines = f.readlines()
    n_lines = len(lines)

    for i, line in enumerate(lines):
        logging.info(f'Reading line {i+1}/{n_lines}')

        logging.debug(f'Splitting to columns')
        raw_columns = line.split(separator)
        named_columns = {}

        for i, column_name in enumerate(columns):
            named_columns[column_name] = raw_columns[i]

        logging.debug(named_columns)

        logging.debug(f'Getting row index')
        index = named_columns[index_column]

        if begin is not None and not begin_reached:
            logging.info(f'Skipping line {index}')
            if index == begin:
                logging.info(f'Begin reached ({index})')
                begin_reached = True

            continue

        logging.debug(f'Getting target column value')

        target_column_text = named_columns[column_to_search].lower()

        words_found = False
        total_weight = 0

        logging.debug(f'Looking up for words in target column')

        for word, weight in words_w_weights.items():
            idx = 0

            regex = '' 
            DELIMITES_RE = '[ .,;|"\']'

            if search_mode == 'regex':
                regex = re.compile(word)
            elif search_mode == 'words':
                regex = re.compile(DELIMITES_RE + word + DELIMITES_RE)
            else:
                raise Exception(f'Unsupported seach mode: {search_mode}')
           
            m = regex.search(target_column_text)
            if m:
                logging.debug(f'Found word: {word}')

                logging.debug(f'Adding it\'s weight')
                total_weight += words_w_weights.get(word, 0)

                words_before = re.split(DELIMITES_RE, target_column_text[:m.start()])[-suffix_max_padding:]
                words_after = re.split(DELIMITES_RE, target_column_text[m.end():])[1:idx+suffix_max_padding]

                potential_suffixes = [*words_before, *words_after]

                logging.debug(f'Potential suffixes:')
                logging.debug(potential_suffixes)
                logging.debug(f'Calculating weight')
                total_weight += sum(
                    map(lambda suffix: suffixes_w_weights.get(suffix, 0), 
                        filter(lambda maybe_suff: maybe_suff in suffixes_w_weights.keys(), potential_suffixes)
                    )
                )

                words_found = True

        if words_found:
            logging.debug(f'As words have been matched -> adding an output line')
            with open(output_file, 'a') as f:
                f.write(line.replace('\n', '') + separator + str(total_weight) + '\n')

        logging.debug(f'Writing down finished md5 to')
        with open(progress_file, 'w') as f:
            f.write(index)

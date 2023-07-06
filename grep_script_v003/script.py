import argparse
from pprint import pprint
import logging
import sys
import os
import re

from utils import parse_config

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(message)s')

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-i', '--input_file', required=True, help='input file')
parser.add_argument('-o', '--output_file', default=os.path.join(SCRIPT_DIR, 'out.txt'), help='output file')
parser.add_argument('-s', '--search_config', required=True, help='seacrh config file')
parser.add_argument('-c', '--config', default=os.path.join(SCRIPT_DIR, 'config.ini'), help='config file')
parser.add_argument('-t', '--type', default='new', help='old or new config type')
parser.add_argument('-w', '--weights', help='words/suffixes weights file')
parser.add_argument('-b', '--begin', help='start with specific input line')
parser.add_argument('-p', '--progress_file', default=os.path.join(SCRIPT_DIR, '.last_success_md5.tmp.txt'), help='file for last succeffsully finsihed md5 record')

input_args = parser.parse_args()

logging.info('Parsing args')

input_file = input_args.input_file
output_file = input_args.output_file
search_config = input_args.search_config
config = input_args.config
config_type = input_args.type
filepath_weights_csv = input_args.weights
begin = input_args.begin
progress_file = input_args.progress_file

logging.info('Command line args (including defaults):')
logging.info(input_args)

logging.info('Check if input file exists (expected: true)')
if not os.path.exists(input_file):
    raise Exception(f'Input file doesn\'t exists ({input_file})')

logging.info('Check if output file exists (expected: false)')
if not os.path.exists(output_file):
    logging.warning(f'WARNING Output file exists - will be overwriten')

args = parse_config(config, search_config, config_type, filepath_weights_csv)
suffixes_w_weights = {}
words_w_weights = {}

for row in args["weights"]:
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
        raw_columns = line.split(args["separator"])
        named_columns = {}

        for i, column_name in enumerate(args["columns"]):
            named_columns[column_name] = raw_columns[i]

        logging.debug(named_columns)

        logging.debug(f'Getting row index')
        index = named_columns[args["index_column"]]

        if begin is not None and not begin_reached:
            logging.info(f'Skipping line {index}')
            if index == begin:
                logging.info(f'Begin reached ({index})')
                begin_reached = True

            continue

        logging.debug(f'Getting target column value')

        target_column_text = named_columns[args["column_to_search"]].lower()

        words_found = False
        total_weight = 0

        logging.debug(f'Looking up for words in target column')

        for word, weight in words_w_weights.items():
            idx = 0

            regex = '' 
            DELIMITES_RE = '[ .,;|"\']'

            if args["search_mode"] == 'regex':
                regex = re.compile(word)
            elif args["search_mode"] == 'words':
                regex = re.compile(DELIMITES_RE + word + DELIMITES_RE)
            else:
                raise Exception(f'Unsupported seach mode: {args["search_mode"]}')
           
            m = regex.search(target_column_text)
            if m:
                logging.debug(f'Found word: {word}')

                logging.debug(f'Adding it\'s weight')
                total_weight += words_w_weights.get(word, 0)

                words_before = re.split(DELIMITES_RE, target_column_text[:m.start()])[-args["suffix_max_padding"]:]
                words_after = re.split(DELIMITES_RE, target_column_text[m.end():])[1:idx+args["suffix_max_padding"]]

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
                f.write(line.replace('\n', '') + args["separator"] + str(total_weight) + '\n')

        logging.debug(f'Writing down finished md5 to')
        with open(progress_file, 'w') as f:
            f.write(index)

from configparser import ConfigParser
import logging
import toml
import csv
from typing import TypedDict, Union


class Config(TypedDict):
    separator: str
    columns: list
    index_column: Union[str, int]
    suffix_max_padding: int
    column_to_search: Union[str, int, list]
    search_mode: str
    weights: list
    

def read_config(filepath):
    config = ConfigParser()
    res = config.read(filepath)

    if not res:
        raise Exception(f'Not able to read .ini file from: {filepath}')

    return config


def read_old_config(filepath):
    config = toml.load(filepath)

    if not config:
        raise Exception(f'Not able to read .toml file from: {filepath}')

    return config


def parse_config(config, search_config, config_type, weights_filepath):
    logging.info(f'Designated config type: {config_type}')

    if config_type == 'old':
        logging.info('Parsing config')

        config = read_old_config(search_config)
        separator = config["separator"]
        index_column = 0
        suffix_max_padding = config["distance"]["default"]
        field = config["field"]

        if isinstance(field, list):
            column_to_search = field[0]
        else:
            column_to_search = field

        columns = list(range(column_to_search + 1))
        search_mode = "regex"
        weights = [[config["rule"]["text"], config["rule"]["weight"], '1']]
        weights += [[k, v["weight"], '0'] for k, v in config["suffix"].items()]

    elif config_type == 'new':
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
        if weights_filepath is None:
            raise Exception("Weights filepath not given")
        with open(weights_filepath) as f:
            weights = [row for row in csv.reader(f, delimiter=',')]
    else:
        raise Exception(f'Unknown config type: {config_type}')

    return Config(
        separator=separator,
        columns=columns,
        index_column=index_column,
        suffix_max_padding=suffix_max_padding,
        column_to_search=column_to_search,
        search_mode=search_mode,
        weights=weights
    )

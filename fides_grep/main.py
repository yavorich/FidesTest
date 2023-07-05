"""
==================================================
Copyright (c) 2022 Gnifajio None [gnifajio@gmail.com].
All Rights Reserved.
==================================================
"""

import logging
from os.path import exists as exists_data
import os

from analyzer import analyse_file
from config_loader import arguments_loader, Config

if __name__ == '__main__':
    args = arguments_loader.parse_args()
    config = Config(args.config)

    if args.log.lower() == 'info':
        log_level = logging.INFO
    elif args.log.lower() == 'debug':
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)

    if os.path.isdir(args.input):
        if args.destination:
            destination = args.destination
            if not exists_data(destination):
                os.makedirs(destination)
        else:
            destination = f'{args.input}_{config.extension}'
            if not exists_data(destination):
                os.makedirs(destination)

        for file in os.listdir(args.input):
            analyse_file(args.input, config, destination=destination)
    elif exists_data(args.input):
        analyse_file(args.input, config)
    else:
        logging.critical(f'Invalid name {repr(args.input)}')
        exit(1)

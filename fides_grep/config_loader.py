import argparse
import logging

import toml
import re
from collections import namedtuple


def normalize_extension(extension: str):
    if extension.startswith('.'):
        return extension
    else:
        return f'.{extension}'


class ConfigurationError(BaseException):
    pass


class Distance:
    default_left = 0
    default_right = 0

    def __init__(self, default=None, left=None, right=None):

        if left is None:
            left = self._get_default_left(default)
        if right is None:
            right = self._get_default_right(default)

        self.left = left
        self.right = right

    @classmethod
    def _get_default_left(cls, default):
        if default:
            return default
        elif cls.default_left is not None:
            return cls.default_left

    @classmethod
    def _get_default_right(cls, default):
        if default:
            return default
        elif cls.default_right is not None:
            return cls.default_right

    def __repr__(self):
        return f'{self.__class__.__name__}(left = {self.left}, right = {self.right},' \
               f'default = {self.default_left, self.default_right}'


class Config:
    def __init__(self, filename: str = 'config.toml'):
        config = toml.load(filename)
        self.normalize = config.get('normalize', True)
        suffix = namedtuple('Suffix', 'word weight distance')
        self.separator: str = config['separator']
        self.extension: str = normalize_extension(config['extension'])
        field = config['field']

        if isinstance(field, int):
            self.fields = [field]
        elif isinstance(field, list):
            self.fields = field
        else:
            raise ConfigurationError('field must be list or integer')
        self.mode = config['rule']['mode']
        self.weight = config['rule']['weight']

        try:
            dist = config['distance']
            default = dist['default']
            left = dist.get('left')
            right = dist.get('right')
            if left is None:
                left = default
            if right is None:
                right = default

            Distance.default_left = left
            Distance.default_right = right

            self.distance = Distance(default=default, )

        except KeyError:
            logging.critical('distance.default is not defined')
            exit(2)

        rule = config['rule']['text']
        if self.mode == 'w':
            rule = r'\b' + rule + r'\b'
        elif self.mode != 'E':
            raise ConfigurationError(f'invalid mode {repr(self.mode)}')
        self.rule = re.compile(f'({rule})')

        self.suffixes = [
            suffix(re.compile(k), v['weight'], Distance(**v.get('distance', self.distance.__dict__)))
            for k, v in config['suffix'].items()
        ]
        assert isinstance(self.separator, str), 'separator must be string'
        assert isinstance(self.extension, str), 'extension must be string'
        assert isinstance(self.fields, list), 'field must be integer'
        assert isinstance(self.weight, int), 'weight must be integer'
        for suffix in self.suffixes:
            assert isinstance(suffix.weight, int), 'suffix.weight must be integer'


arguments_loader = argparse.ArgumentParser(description=__doc__)
arguments_loader.add_argument(
    'input',
    type=str,
    help='The path to the file or folder to analyze'
)
# arguments_loader.add_argument(
#     'output',
#     type=str,
#     help='Path to the resulting file'
# )
arguments_loader.add_argument(
    '--config',
    '-c',
    type=str,
    default='config.toml',
    help='The path to the configuration file'
)

arguments_loader.add_argument(
    '--destination',
    '-d',
    type=str,
    default='.',
    help='The path to the file or folder to output'
)

arguments_loader.add_argument(
    '--log',
    type=str,
    default='info',
    help='The path to the configuration file'
)

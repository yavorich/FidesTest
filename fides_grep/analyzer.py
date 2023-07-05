import logging
import os.path

from config_loader import Config


def get_field_weight(line: str, config: Config) -> int:
    if config.normalize:
        line = line.lower()

    weight = 0
    keywords = config.rule.finditer(line)

    for keyword in keywords:
        weight += config.weight
        for suffix in config.suffixes:
            weight += sum(1 for _ in
                          suffix.word.finditer(
                              line,
                              keyword.start() - suffix.distance.left,
                              keyword.start() + suffix.distance.right
                          )
                          )
    return weight

    # finds = len(config.rule.findall(line.lower()))
    # if finds > 0:
    #     weight = config.weight * finds
    #     for suffix in config.suffixes:
    #         weight += sum([suffix.weight for _ in suffix.word.findall(line.lower())])
    #     return weight
    # return 0


def analyse_file(filename: str, config: Config, destination='.'):
    logging.info(f'Starting analyze file {filename}')
    file_path = os.path.join(destination, f'{os.path.splitext(filename)[0]}.{config.extension}')
    open(file_path, 'w').close()
    with open(filename, 'r') as input_file:
        for line_number, line in enumerate(input_file):
            line = line.strip()
            all_fields = line.split(config.separator)
            result = []
            weight = 0
            for n, field in enumerate(all_fields):
                if n in config.fields:
                    weight += get_field_weight(field, config)
                result.append(field)
            if weight > 0:
                result.append(str(weight))
                with open(file_path, 'a') as res_file:
                    res_file.write(config.separator.join(result) + '\n')
    logging.info(f'Finish analyze file {filename}')

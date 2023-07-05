from configparser import ConfigParser

def read_config(filepath):
    config = ConfigParser()
    res = config.read(filepath)

    if not res:
        raise Exception(f'Not able to read .ini file from: {filepath}')

    return config

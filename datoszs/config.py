from threading import currentThread
import json
import yaml
import os


_CONFIG = {}
_CONFIG_PATH = None


def get_config(key, default=None, required=False):
    config = _load_config()
    keys = key.split('.')
    for k in keys:
        if config is None:
            break
        config = config.get(k)
    if config is None:
        config = os.getenv(key.replace('.', '_').upper())
    if config is None:
        if required:
            raise Exception("There is no key [{}] in configuration.".format(key))
        return default
    return config


def get_config_path():
    return _CONFIG_PATH


def set_config_path(path):
    global _CONFIG_PATH
    _CONFIG_PATH = path


def _load_config():
    if _CONFIG_PATH is None:
        return {}
    if currentThread() not in _CONFIG:
        config_path = get_config_path()
        with open(config_path, 'r', encoding='utf8') as config_data:
            if config_path.endswith('.json'):
                loaded = json.load(config_data, )
            elif config_path.endswith('.yaml'):
                loaded = yaml.load(config_data)
            else:
                raise Exception('There is no support for *.%s files' % config_path.split('.')[-1])
            _CONFIG[currentThread()] = loaded
    return _CONFIG[currentThread()]

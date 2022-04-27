import os
import configparser
import logging

logger = logging.getLogger()

def get_config(root_path:str):
    ano_cfg = {}

    config = configparser.ConfigParser()
    config.optionxform = str

    config.read(os.path.join(root_path,
                             "AP_API_Router/API-SERVICE/conf/config.ini"))#, encoding='utf-8')
    for section in config.sections():
        ano_cfg[section] = {}
        for option in config.options(section):
            ano_cfg[section][option] = config.get(section, option)

    return ano_cfg

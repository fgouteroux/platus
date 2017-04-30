# -*- coding: utf-8 -*-
import yaml

def from_yaml(config_file):
    with open(config_file) as fread:
        data = yaml.load(fread)
    return data


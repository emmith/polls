#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Mr Wang'

import yaml
import argparse
import pathlib
import sys

from trafaret_config import commandline

from aiohttpdemo_polls.utils import TRAFARET

# 配置文件路径
BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'polls.yaml'


def get_config(argv=None):
    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        ap,
        default_config=DEFAULT_CONFIG_PATH
    )

    # ignore unknown options
    options, unknown = ap.parse_known_args(argv)
    config = commandline.config_from_options(options, TRAFARET)
    return config


if __name__ == '__main__':
    config = get_config(sys.argv[1:])
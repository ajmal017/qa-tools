#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging

def set_warning():
    manager = logging.Logger.manager
    manager.root.setLevel(logging.WARNING)

    # Iterate loggers and set level based on filename pattern?
    #for k in manager.loggerDict.keys():

def set_debug():
    manager = logging.Logger.manager
    manager.root.setLevel(logging.DEBUG)


def set_info():
    manager = logging.Logger.manager
    manager.root.setLevel(logging.INFO)

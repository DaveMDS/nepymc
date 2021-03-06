#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
#
# Copyright (C) 2010-2019 Davide Andreoli <dave@gurumeditation.it>
#
# This file is part of NEPYMC, a free Media Center written in Python.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import configparser


def LOG(*args):
    print('INI:', *args)


_config = configparser.RawConfigParser()


def read_from_files(files):
    readed = _config.read(files)
    LOG('Readed config from files:')
    for f in readed:
        LOG(' * ' + f)


def write_to_file(file):
    LOG('Writing config to file: ' + file)
    with open(file, 'w') as configfile:
        _config.write(configfile)


def setup_defaults():
    s = 'general'
    add_section(s)
    if not _config.has_option(s, 'show_mature_contents'):
        _config.set(s, 'show_mature_contents', 'False')
    if not _config.has_option(s, 'download_folder'):
        _config.set(s, 'download_folder', os.path.expanduser('~/Download'))
    if not _config.has_option(s, 'max_concurrent_download'):
        _config.set(s, 'max_concurrent_download', '3')

    s = 'backend'
    add_section(s)
    if not _config.has_option(s, 'mainloop'):
        _config.set(s, 'mainloop', 'qt')
    if not _config.has_option(s, 'gui'):
        _config.set(s, 'gui', 'qt')


def add_section(section):
    if not _config.has_section(section):
        _config.add_section(section)


def has_section(section):
    return _config.has_section(section)


def has_option(section, option):
    return _config.has_option(section, option)


def has_options(options):
    raise NotImplementedError("NEED TO BE CHECKED, IMPL SEEMS WRONG")
    # for option in options:
    #     if not _config.has_option(option):
    #         return False
    # return True


def get_options(section):
    return _config.items(section)


def get(section, option, default_value=None):
    if _config.has_option(section, option):
        return _config.get(section, option)

    if default_value is not None:
        set(section, option, default_value)
        return default_value


def set_default(section, option, default_value):
    if not _config.has_option(section, option):
        set(section, option, default_value)


def get_string_list(section, option, separator=' '):
    if not _config.has_option(section, option):
        return []
    string = get(section, option)
    ret = []
    for s in string.split(separator):
        if len(s) > 0:
            ret.append(s if separator == ' ' else s.strip())
    return ret


def get_int(section, option):
    return _config.getint(section, option)


def get_float(section, option):
    return _config.getfloat(section, option)


def get_bool(section, option):
    return _config.getboolean(section, option)


def get_string(section, option):
    return str(_config.get(section, option))


def set(section, option, value):
    _config.set(section, option, str(value))


def set_string_list(section, option, values, separator=' '):
    string = separator.join(values)
    set(section, option, string)


def remove_option(section, option):
    _config.remove_option(section, option)

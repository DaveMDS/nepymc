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
from typing import Tuple

try:
    from xdg.BaseDirectory import xdg_config_home as XDG_CONFIG_HOME
    from xdg.BaseDirectory import xdg_cache_home as XDG_CACHE_HOME
except ImportError:
    XDG_CONFIG_HOME = None
    XDG_CACHE_HOME = None


def LOG(*args):
    print('UTILS:', *args)


def DBG(msg):
    # print('UTILS: %s' % msg)
    pass


# base emc folder
emc_base_dir = os.path.abspath(os.path.dirname(__file__))
LOG('Running from:', emc_base_dir)

# user config folder (xdg or default)
if XDG_CONFIG_HOME and os.path.exists(XDG_CONFIG_HOME):
    user_conf_dir = os.path.join(XDG_CONFIG_HOME, 'emc')
else:
    user_conf_dir = os.path.expanduser('~/.config/emc')
LOG('Config folder:', user_conf_dir)

# user cache folder (xdg or default)
if XDG_CACHE_HOME and os.path.exists(XDG_CACHE_HOME):
    user_cache_dir = os.path.join(XDG_CACHE_HOME, 'emc')
else:
    user_cache_dir = os.path.expanduser('~/.cache/emc')
LOG('Cache folder:', user_cache_dir)


def get_resource(*resource: str) -> str:
    """ Return the full path for the given resource

    Params:
        *resource (str): components of the resource to search (dirs and file name)

    Return (str):
        The full path for the given resource, or None if not found

    Example:
        get_resource('themes', 'default', 'main_window.qml')

    """
    # search in user config dir
    f = os.path.join(user_conf_dir, *resource)
    if os.path.exists(f):
        return f

    # or in the package base dir
    f = os.path.join(emc_base_dir, *resource)
    if os.path.exists(f):
        return f

    # not found :(
    return None

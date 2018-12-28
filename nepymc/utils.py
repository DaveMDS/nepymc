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
import importlib
from abc import ABC

from nepymc import ini

try:
    from xdg.BaseDirectory import xdg_config_home as XDG_CONFIG_HOME
    from xdg.BaseDirectory import xdg_cache_home as XDG_CACHE_HOME
except ImportError:
    XDG_CONFIG_HOME = None
    XDG_CACHE_HOME = None


def LOG(*args):
    print('UTILS:', *args)


def DBG(*args):
    # print('UTILS:', *args)
    pass


# base emc package folder
emc_base_dir = os.path.abspath(os.path.dirname(__file__))
LOG('Running from:', emc_base_dir)

# user config folder (xdg or default)
if XDG_CONFIG_HOME:
    user_conf_dir = os.path.join(XDG_CONFIG_HOME, 'emc')
else:
    user_conf_dir = os.path.expanduser('~/.config/emc')
LOG('Config folder:', user_conf_dir)

# user cache folder (xdg or default)
if XDG_CACHE_HOME:
    user_cache_dir = os.path.join(XDG_CACHE_HOME, 'emc')
else:
    user_cache_dir = os.path.expanduser('~/.cache/emc')
LOG('Cache folder:', user_cache_dir)


def get_resource(*resource: str) -> str:
    """ Return the full path for the given resource

    Params:
        *resource (str): components of the resource to search (dirs and fname)

    Return (str):
        The full path for the given resource, or an empty string on errors

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
    return ''


class Singleton(object):
    __single = None

    def __new__(cls, *args, **kwargs):
        if cls != type(cls.__single):
            cls.__single = object.__new__(cls, *args, **kwargs)
        return cls.__single


class EmcBackendableABC(ABC):
    """ TODO DOC """

    backendable_pkg = 'Subclass MUST override'  # fe: 'mainloop', 'gui'
    backendable_cls = 'Subclass MUST override'  # fe: 'EmcMainLoop', 'EmcDialog'

    def __new__(cls, *args, **kargs):

        # get the backend to use from ini [backend] backendable_pkg
        backend_name = ini.get('backend', cls.backendable_pkg)
        if backend_name is None:
            raise RuntimeError(
                'Cannot find backend "%s" in ini file section "backend"' %
                cls.backendable_pkg)

        # import the backend package (fe: nepymc.mainloop.qt)
        pkg_name = '.'.join(('nepymc', cls.backendable_pkg, backend_name))
        pkg = importlib.import_module(pkg_name)

        # instantiate the class from the backend package
        pkg_cls = getattr(pkg, cls.backendable_cls)
        return super().__new__(pkg_cls)

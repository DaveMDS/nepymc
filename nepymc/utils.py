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
import getpass
import re
import importlib
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Tuple, Dict

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
    user_conf_dir = os.path.join(XDG_CONFIG_HOME, 'nepymc')
else:
    user_conf_dir = os.path.expanduser('~/.config/nepymc')
LOG('Config folder:', user_conf_dir)

# user cache folder (xdg or default)
if XDG_CACHE_HOME:
    user_cache_dir = os.path.join(XDG_CACHE_HOME, 'nepymc')
else:
    user_cache_dir = os.path.expanduser('~/.cache/nepymc')
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


def cache_path_for_url(url: str):
    fname = md5(url)
    return os.path.join(user_cache_dir, 'remotes', fname[:2], fname)


def utf8_to_markup(string):
    # TODO what to do here ?? should be backend specific?
    return string


def url2path(url):
    # TODO ... convert the url to a local path !!
    return url[7:]


def hum_size(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.3fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.1fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.0fK' % kilobytes
    else:
        size = '%.0fb' % bytes
    return size


def millis_to_duration(millis, hours=False):
    """Convert the number of milliseconds in a readable duration
       hours: If True then hours will be visible also when < 1
    """
    seconds = millis / 1000.0
    h = seconds // 3600
    m = (seconds // 60) % 60
    s = seconds % 60
    if h > 0 or hours:
        return '%d:%02d:%02d' % (h, m, s)
    else:
        return '%d:%02d' % (m, s)


def splitpath(path):
    """ Convert a string path in a list of all the components """
    return [p for p in path.split(os.path.sep) if p != '']


def ensure_file_not_exists(fullpath):
    """ Add a number at the end of the file name to ensure it do not exists """
    if not os.path.exists(fullpath):
        return fullpath

    num = 1
    name, ext = os.path.splitext(fullpath)
    while True:
        new = name + '_%03d' % num + ext
        if not os.path.exists(new):
            return new
        num += 1


def md5(txt):
    """ calc the md5 of the given str """
    txt = bytes(txt, 'utf-8')
    return hashlib.md5(txt).hexdigest()


def user_name():
    return getpass.getuser()


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def natural_cmp(a, b):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    x = [convert(c) for c in re.split('([0-9]+)', a)]
    y = [convert(c) for c in re.split('([0-9]+)', b)]
    if x == y:
        return 0
    elif x > y:
        return 1
    else:
        return -1


def clamp(val, lower, upper):
    return lower if val < lower else upper if val > upper else val


class Singleton(object):
    __single = None

    def __new__(cls, *args, **kwargs):
        if cls != type(cls.__single):
            cls.__single = object.__new__(cls, *args, **kwargs)
        return cls.__single


class EmcBackendableABC(ABC):
    """ TODOC """

    backendable_pkg = 'Subclass MUST override'  # fe: 'mainloop', 'gui'
    backendable_cls = 'Subclass MUST override'  # fe: 'EmcTimer', 'EmcDialog'

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


class EmcObject(ABC):
    """ Base class for all emc objects

    The purpose of this class is to standardize the object lifetime
    management for all different objects.

    Basically there are two way to create objects: with or without a parent.

    With a parent:
    If you pass a parent (EmcObject) in the constructor then the parent object
    will become the owner of the object, parent keep a children list and thus
    will keep the child alive until the parent is deleted. Deleting an object
    will also delete all it's children.

    Without a parent:
    If you don't give a parent in the constructor you MUST keep a reference
    to the object to keep it alive and you are responsable of deleting
    the object when appropriate.

    In the case you are keeping a reference to an object (both with a parent
    or not) it is advisable to monitor the deletion of the object using
    the on_delete function to be notifyed on object deletion and thus
    remove your reference, that will otherwise become invalid.

    Keep in mind that, also if you are keeping a reference to an object, is
    it still possible that it will be deleted "under your feet" (fe a dialog
    can be deleted by the user pressing the BACK key). The on_delete callback
    should always be used when keeping references.

    Params:
        parent (EmcObject): the owner object

    Properties (READONLY):
        parent (EmcObject): the owner object
        children (list): list of EmcObject that are direct children
        deleted (bool): whenever the object has been already deleted

    """

    def __init__(self, parent: Optional['EmcObject'] = None):
        # public "readonly" properties
        self.parent: Optional['EmcObject'] = parent
        self.children: List['EmcObject'] = []
        self.deleted: bool = False

        # private members
        self._del_cbs: List[Tuple[Callable, Dict]] = []  # list of (cb, kargs)

        if parent is not None:
            if not isinstance(parent, EmcObject):
                raise TypeError('EmcObject parent MUST be an EmcObject')
            parent.children.append(self)

        print("__init__()", self)

    # TODO THIS IS ONLY FOR DEBUG, SHOULD BE REMOVE FOR RELEASE !!!
    def __del__(self):
        print("__del__()", self)
        # if not self.deleted:
        #     self.delete()
        if not self.deleted:
            raise RuntimeError('Deleting before delete()')
        if self.children:
            raise RuntimeError('Deleting a parent with live children')

    def __repr__(self):
        return '<{} children:{} parent:{}>'.format(
               self.__class__.__name__, len(self.children), self.parent)

    @abstractmethod
    def delete(self) -> bool:
        """ Delete the object and free all internal resources.

        This call will recursively delete() all children objects, set the
        deleted flag to True and at the end will call the user defined callbacks

        return (bool):
            True if the object is been deleted or False otherwise (fe the
            object was already deleted)

        """
        print("delete()", self)

        # never delete twice
        if self.deleted:
            print('WARNING: Object already deleted', self)
            return False

        # delete all child objects
        # reversed because child.delete() will remove from the walked list
        for child in reversed(self.children):
            child.delete()

        # remove ourself from the parent children list
        if self.parent:
            self.parent.children.remove(self)

        # mark the object as already deleted
        self.deleted = True

        # call the user on_delete callbacks
        for cb, kargs in self._del_cbs:
            cb(self, **kargs)

        return True

    def on_delete(self, callback: Callable, **kargs) -> None:
        """ Add a new callback to be called on object deletion

        Params:
            callback (callable): the function to call on object deletion
            **kargs: Any other keywords arguments will be passed back
                     in the callback as keyword arguments

        Callback signature:
            func(obj, **kargs)

        """
        self._del_cbs.append((callback, kargs))

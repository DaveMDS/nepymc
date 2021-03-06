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

import sys
import os
import shelve
import glob
from queue import Queue

from nepymc import utils
from nepymc.gui import EmcDialog
from nepymc.mainloop import EmcTimer


def DBG(*args):
    # print('SDB:', *args)
    pass


_queue = None
_queue_timer = None
_instances = []


class EmcDatabase(object):
    """ TODOC """

    def __init__(self, name, version=None):
        self._name = name
        self._vers = version
        self._vkey = '__database__version__'
        self._sync_timer = None

        # build the db name (different db for py2 and py3)
        dbname = os.path.join(utils.user_conf_dir,
                              'db_py%d_%s' % (sys.version_info[0], name))
        DBG('Open db: ' + name + ' from file: ' + dbname)

        # check if the db exist (or is the first time we use it)
        first_run = False if glob.glob(dbname + '*') else True

        # open the shelve
        self._sh = shelve.open(dbname)

        if (not first_run) and (version is not None) and (
                self.get_version() != version):
            # the db is outdated
            text = _(
                '<b>The database %s is outdated!</b><br><br>'
                'The old file has been renamed with a .backup extension and '
                'a new (empty) one has been created.<br><br>Sorry for the incovenience.') % (
                name)
            EmcDialog(style='warning', title=_('EpyMC Database'), text=text)

            # close the shelve
            self._sh.close()

            # rename db files to .backup
            for fname in glob.glob(dbname + '*'):
                os.rename(fname, fname + '.backup')

            # reopen a new (empty) shelve
            self._sh = shelve.open(dbname)

        if version is not None:
            # store the version inside the db
            self._sh[self._vkey] = version

        _instances.append(self)

    def _close(self):
        DBG('Closing database %s' % self._name)
        if self._sync_timer is not None:
            self._sync_timer.delete()
            self._sync_timer = None
        self._sh.close()

    def __len__(self):
        if self._vers:
            return len(self._sh) - 1
        else:
            return len(self._sh)

    def __contains__(self, key):
        return key in self._sh

    def __iter__(self):
        return self.items()

    def items(self):
        for k, v in self._sh.items():
            if k != self._vkey:
                yield k, v

    def keys(self):
        if self._vers:
            return [k for k in self._sh.keys() if k != self._vkey]
        else:
            return self._sh.keys()

    def get_data(self, key):
        DBG('Get Data for db: %s, key: %s' % (self._name, key))
        return self._sh[key]

    def set_data(self, key, data, thread_safe=False):
        DBG('Set data for db: %s, id: %s' % (self._name, key))
        if thread_safe:
            # just put in the queue
            _queue.put((self, key, data))
        else:
            # update the db now
            self._sh[key] = data
            self._delayed_sync()

    def del_data(self, key):
        if key in self._sh:
            del self._sh[key]
            self._delayed_sync()

    def id_exists(self, key):
        return key in self._sh

    def get_version(self):
        if self._vkey in self._sh:
            return self._sh[self._vkey]

    def dump(self):
        import pprint
        print('=' * 60)
        print('DB NAME: "{}" - VERSION: {}'.format(self._name, self._vers))
        print('=' * 60)
        for key in self._sh.keys():
            print('\nDB KEY: "{}"'.format(key))
            pprint.pprint(self._sh[key])
        print('=' * 60)

    def _delayed_sync(self):
        if self._sync_timer is None:
            self._sync_timer = EmcTimer(5.0, self._sync_timer_cb, oneshot=True)
        else:
            self._sync_timer.reset()

    def _sync_timer_cb(self):
        DBG("Syncing database %s" % self._name)
        self._sh.sync()
        self._sync_timer = None


##################


def init():
    global _queue
    global _queue_timer

    _queue = Queue()

    _queue_timer = EmcTimer(0.2, _process_queue)


def shutdown():
    global _queue
    global _queue_timer

    _queue_timer.delete()
    del _queue

    for db in _instances:
        db._close()


def _process_queue():
    global _queue

    if _queue.empty():
        return True

    count = 10
    # DBG("Queue size: " + str(_queue.qsize()))
    while not _queue.empty() and count > 0:
        # DBG('Queue processing...count:%d  len:%d' % (count, _queue.qsize()))
        count -= 1
        (db, key, data) = _queue.get_nowait()
        db._sh[key] = data
    db._delayed_sync()

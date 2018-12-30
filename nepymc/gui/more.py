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

from nepymc import ini
from nepymc import utils
from nepymc import storage
from nepymc.gui import EmcDialog


class EmcFolderSelector(object):
    """
    Open a dialog that allow the user to choose a path on the filesystem.

    Args:
       title:
          The (optional) dialog title.
       done_cb:
          The (mandatory) function to call when the selection is done.
          Signature: func(path, **kargs)
       **kargs:
          Any other keyword arguments will be passed back in the done_cd func
    """

    def __init__(self, title=None, done_cb=None, **kargs):
        self._user_cb = done_cb
        self._user_kargs = kargs

        self._dialog = EmcDialog(title or _('Source Selector'), style='list')
        self._dialog.button_add(_('Select'), self._btn_select_cb)
        self._dialog.button_add(_('Browse'), self._btn_browse_cb, default=True)

        self.populate_devices()

    def populate_devices(self):
        self._dialog.list_clear()

        # other storage devices
        for dev in storage.list_devices():
            if dev.is_mounted:
                it = self._dialog.list_item_append(dev.label, dev.icon)
                it.data['root'] = it.data['path'] = dev.mount_point
        self._dialog.list_go()

    def populate_folder(self, root, folder):
        if folder == '':  # back in '/'
            self.populate_devices()
            return

        try:
            folders = os.listdir(folder)
        except PermissionError:
            EmcDialog(style='error', text=_('Permission denied'))
            return

        self._dialog.list_clear()

        # back item
        parent = os.path.normpath(os.path.join(folder, '..'))
        it = self._dialog.list_item_append(_('Back'), 'icon/back')
        it.data['root'] = root
        it.data['path'] = parent if parent != folder else ''  # back in '/'

        # folders
        for fname in utils.natural_sort(folders):
            fullpath = os.path.join(folder, fname)
            if fname[0] != '.' and os.path.isdir(fullpath):
                it = self._dialog.list_item_append(fname, 'icon/folder')
                it.data['root'] = root
                it.data['path'] = fullpath

        self._dialog.list_go()

    def _btn_browse_cb(self, btn):
        it = self._dialog.list_item_selected_get()
        if len(it.data['path']) < len(it.data['root']):
            self.populate_devices()
        else:
            self.populate_folder(it.data['root'], it.data['path'])

    def _btn_select_cb(self, btn):
        path = self._dialog.list_item_selected_get().data['path']
        if path and callable(self._user_cb):
            self._user_cb('file://' + path, **self._user_kargs)
        self._dialog.delete()


class EmcSourcesManager(object):
    """ Open a dialog that allow the user to manage (add/remove) source
    folders. The manager automatically get the folders list from config file,
    using the group passed in the contructor and the 'folders' config item.
    The config item is also automatically updated when finished.

    Args:
       conf_group:
          The name of the config section to read the folders list from.
       title:
          Optional title for the dialog.
       done_cb:
          Function called when the user press the 'done' button.
          Signature: cb(new_folders_list)
    """

    def __init__(self, conf_group, title=None, done_cb=None):
        # EmcDialog.__init__(self, title, style='list')
        self._dialog = dia = EmcDialog(title or _('Sources Manager'),
                                       style='list')
        dia.button_add(_('Done'), icon='icon/ok',
                       selected_cb=self._cb_btn_done)
        dia.button_add(_('Add'), icon='icon/plus',
                       selected_cb=self._cb_btn_add)
        dia.button_add(_('Remove'), icon='icon/minus',
                       selected_cb=self._cb_btn_remove)
        self._sources = ini.get_string_list(conf_group, 'folders', ';')
        self._conf_group = conf_group
        self._done_cb = done_cb
        self._populate()

    def _populate(self):
        self._dialog.list_clear()
        for src in self._sources:
            self._dialog.list_item_append(src, 'icon/folder')
        self._dialog.list_go()

    def _cb_btn_add(self, btn):
        EmcFolderSelector(title=_('Choose a new source'),
                          done_cb=self._cb_selected)

    def _cb_btn_remove(self, btn):
        it = self._dialog.list_item_selected_get()
        if it and it.label in self._sources:
            self._sources.remove(it.label)
            self._populate()

    def _cb_selected(self, path):
        if path not in self._sources:
            self._sources.append(path)
            self._populate()

    def _cb_btn_done(self, btn):
        ini.set_string_list(self._conf_group, 'folders', self._sources, ';')
        if callable(self._done_cb):
            self._done_cb(self._sources)
        self._dialog.delete()

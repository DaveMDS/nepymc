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
from typing import Any

# from PySide2.QtCore import Qt, QObject, Slot, QAbstractListModel

from PySide2.QtCore import Qt, Slot, QAbstractListModel

# from nepymc import utils
from nepymc import gui
from nepymc.gui import EmcDialog


def LOG(*args):
    print('GUI_QT:', *args)


def ERR(*args):
    print('GUI_QT ERROR:', *args, file=sys.stderr)


def DBG(*args):
    print('GUI_QT:', *args)
    pass


class DialogListModel(QAbstractListModel):
    label_role = Qt.UserRole + 1
    label_end_role = Qt.UserRole + 2
    icon_role = Qt.UserRole + 3
    icon_end_role = Qt.UserRole + 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []  # list of tuple: (label, icon, end, args, kargs)
        self.current_index = 0

    # Qt model implementation
    def roleNames(self):
        return {
            self.label_role: b'label',
            self.label_end_role: b'label_end',
            self.icon_role: b'icon',
            self.icon_end_role: b'icon_end',
        }

    def rowCount(self, index):
        return len(self.items)

    def data(self, index, role):
        label, icon, end, args, kargs = self.items[index.row()]
        if role == self.label_role:
            return label
        if role == self.label_end_role:
            if end and end.startswith('text/'):
                return end[5:]
        elif role == self.icon_role:
            return icon
        elif role == self.icon_end_role:
            if end and end.startswith('icon/'):
                return end

    # below methods are to be called from QML
    @Slot(int)
    def selection_changed(self, index):
        """ An in item has been selected in QML """
        self.current_index = index


class EmcDialog_Qt(EmcDialog):
    """ PySide2 implementation of the EmcDialog

      style can be 'panel' or 'minimal'
      or you can also apply special style that perform specific task:
         'info', 'error', 'warning', 'yesno', 'cancel', 'progress',
         'list', 'image_list_horiz', 'image_list_vert',
         'buffering'
    """

    def __init__(self, title=None, text=None, content=None, spinner=False,
                 style='panel', done_cb=None, canc_cb=None, user_data=None):
        super().__init__(title, text, content, spinner, style,
                         done_cb, canc_cb, user_data)

        print("INIT DIALOG QT")
        self._list_model = DialogListModel() if style == 'list' else None
        self._buttons = []
        self._gui = gui.gui_instance_get()
        self._qml_obj = self._gui._qml_root.build_dialog(title, style, text,
                                                         content, spinner,
                                                         self._list_model)

        # This is needed to keep the object alive (the qt model in particular)
        # maybe the user don't keep a ref because dialog can auto-delete
        self._auto_reference = self

        # automatic buttons
        if style in ('info', 'error', 'warning'):
            self.button_add(_('Ok'), lambda btn: self.delete())

        if style == 'yesno':
            if self._canc_cb:
                self.button_add(_('No'), lambda btn: self._canc_cb(self))
            else:
                self.button_add(_('No'), lambda btn: self.delete())

            if self._done_cb:
                self.button_add(_('Yes'), lambda btn: self._done_cb(self))
            else:
                self.button_add(_('Yes'), lambda btn: self.delete())

        if style == 'cancel':
            if canc_cb:
                self.button_add(_('Cancel'), lambda btn: self._canc_cb(self))
            else:
                self.button_add(_('Cancel'), lambda btn: self.delete())

    def delete(self) -> None:
        self._auto_reference = None
        self._qml_obj.emcDestroy()

    def main_content_set(self, content) -> None:
        raise NotImplementedError

    def button_add(self, label: str, selected_cb: callable = None,
                   cb_data: Any = None, icon: str = None,
                   default: bool = False) -> None:

        def button_clicked_cb(idx):
            b = self._buttons[idx]
            if b['data']:
                b['cb'](b, b['data'])
            else:
                b['cb'](b)

        newidx = len(self._buttons)
        btn = self._qml_obj.action_add(newidx, label, icon)
        btn.emcButtonClicked.connect(button_clicked_cb)
        self._buttons.append({'btn': btn, 'cb': selected_cb, 'data': cb_data})

    def buttons_clear(self):
        raise NotImplementedError

    def title_set(self, text: str):
        raise NotImplementedError

    def text_set(self, text: str):
        self._qml_obj.setProperty('main_text', text)

    def text_append(self, text: str) -> None:
        raise NotImplementedError

    def list_item_append(self, label: str, icon: str=None, end: str=None,
                         *args, **kargs):
        item_data = (label, icon, end, args, kargs)
        self._list_model.items.append(item_data)

    def list_clear(self):
        self._list_model.beginResetModel()
        self._list_model.items = []
        self._list_model.endResetModel()

    def list_item_selected_get(self):
        return self._list_model.current_index

    def list_item_icon_set(self, it, icon, end=False):
        raise NotImplementedError

    def list_go(self):
        self._list_model.beginResetModel()
        self._list_model.endResetModel()

    def spinner_start(self):
        raise NotImplementedError

    def spinner_stop(self):
        raise NotImplementedError

    def progress_set(self, val: float):
        self._qml_obj.setProperty('progress', val)

    def autoscroll_enable(self, speed_scale: float = 1.0,
                          start_delay: float = 3.0):
        raise NotImplementedError




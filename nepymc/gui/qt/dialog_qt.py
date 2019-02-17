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
from typing import Any, Optional

# from PySide2.QtCore import Qt, QObject, Slot, QAbstractListModel

from PySide2.QtCore import Qt, Slot, QAbstractListModel

# from nepymc import utils
from nepymc.gui import EmcGui
from nepymc.gui import EmcDialog, EmcDialogListItem


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

    def __init__(self, dialog):
        super().__init__(None)
        self.dialog = dialog
        self.items = []  # list of EmcDiaogListItem
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
        it = self.items[index.row()]
        if role == self.label_role:
            return it.label  or ''
        if role == self.label_end_role:
            if it.end and it.end.startswith('text/'):
                return it.end[5:]
        elif role == self.icon_role:
            return it.icon or ''
        elif role == self.icon_end_role:
            if it.end and it.end.startswith('icon/'):
                return it.end
        return ''

    # below methods are to be called from QML
    @Slot(int)
    def selection_changed(self, index):
        """ An item has been selected in QML """
        self.current_index = index

    @Slot(int)
    def item_activated(self, index):
        """ An item has been activated in QML """
        it = self.items[index]
        self.dialog._call_user_done_callback(it)


class EmcDialog_Qt(EmcDialog):
    """ PySide2 implementation of the EmcDialog """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        print("INIT DIALOG QT")
        if self._style in self.list_styles:
            self._list_model = DialogListModel(self)
        else:
            self._list_model = None
        self._buttons = []
        self._gui = EmcGui.instance()
        self._qml_obj = self._gui._qml_root.build_dialog(
                            self._title, self._style, self._text,
                            self._content, self._spinner,
                            self._list_model)
        self._qml_obj.emcQuitRequested.connect(self._quit_requested_cb)

        # automatic buttons
        self._create_auto_buttons()

    def delete(self) -> None:
        super().delete()
        self._qml_obj.emcDestroy()
        self._qml_obj = None

    def _quit_requested_cb(self):
        self._call_user_canc_callback()

    def button_add(self, label: str, selected_cb: callable = None,
                   cb_data: Any = None, icon: str = None,
                   default: bool = False) -> None:

        def button_clicked_cb(idx):
            b = self._buttons[idx]
            if b['data']:
                b['cb'](idx, b['data'])
            else:
                b['cb'](idx)

        newidx = len(self._buttons)
        btn = self._qml_obj.action_add(newidx, label, icon, default)
        btn.emcButtonClicked.connect(button_clicked_cb)
        self._buttons.append({'btn': btn, 'cb': selected_cb, 'data': cb_data})

    def buttons_clear(self):
        self._qml_obj.actions_clear()
        self._buttons = []

    def content_set(self, content: Optional[str]) -> None:
        super().content_set(content)
        self._qml_obj.setProperty('content', content)

    def title_set(self, title: str):
        super().title_set(title)
        self._qml_obj.setProperty('title', title)

    def text_set(self, text: str):
        super().text_set(text)
        self._qml_obj.setProperty('main_text', text)

    def text_append(self, text: str) -> None:
        super().text_append(text)
        self._qml_obj.setProperty('main_text', self._text)

    def list_item_append(self, label: str, icon: str=None, end: str=None,
                         *args, **kargs):
        it = EmcDialogListItem(label, icon, end, args, kargs)
        self._list_model.items.append(it)
        return it

    def list_clear(self):
        self._list_model.beginResetModel()
        self._list_model.items = []
        self._list_model.endResetModel()

    def list_item_selected_get(self):
        idx = self._list_model.current_index
        return self._list_model.items[idx]

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




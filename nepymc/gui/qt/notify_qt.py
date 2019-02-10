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

from PySide2 import QtCore

from nepymc.gui import EmcNotify
from nepymc import gui


class EmcNotify_Qt(EmcNotify):
    """ PySide2 implementation of the EmcNotify """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._model = gui.instance()._notify_model
        self._model.insert_item(self)

    def delete(self):
        super().delete()
        self._model.remove_item(self)

    def text_set(self, text):
        super().text_set(text)
        self._model.update_item(self, [NotifyModel.text_role])

    def image_set(self, image):
        super().image_set(image)
        self._model.update_item(self, [NotifyModel.image_role])


class NotifyModel(QtCore.QAbstractListModel):
    text_role = QtCore.Qt.UserRole + 1
    image_role = QtCore.Qt.UserRole + 2

    role_names = {
        text_role: b'text',
        image_role: b'image',
    }

    def __init__(self):
        super().__init__(None)
        self._items = []  # list of EmcNotify_Qt instances

    def insert_item(self, notify_instance):
        index = len(self._items)
        self.beginInsertRows(QtCore.QModelIndex(), index, index)
        self._items.insert(index, notify_instance)
        self.endInsertRows()

    def remove_item(self, notify_instance):
        index = self._items.index(notify_instance)
        self.beginRemoveRows(QtCore.QModelIndex(), index, index)
        del self._items[index]
        self.endRemoveRows()

    def update_item(self, notify_instance, roles):
        index = self._items.index(notify_instance)
        top_left = self.index(index, 0)
        bottom_right = self.index(index, 0)
        self.dataChanged.emit(top_left, bottom_right, roles)

    #
    #  Qt model implementation
    #

    def roleNames(self):
        return self.role_names

    def rowCount(self, index):
        return len(self._items)

    def data(self, index, role):
        notify_instance = self._items[index.row()]
        if role == self.text_role:
            return notify_instance.text
        elif role == self.image_role:
            return notify_instance.image

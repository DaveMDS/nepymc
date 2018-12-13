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

from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt, QObject, Slot, QAbstractListModel

from nepymc.gui_base import EmcGui_Base
from nepymc import utils
from nepymc import mainmenu


def LOG(*args):
    print('GUI_QT:', *args)


def ERR(*args):
    print('GUI_QT ERROR:', *args, file=sys.stderr)


def DBG(*args):
    print('GUI_QT:', *args)
    pass


class MainMenuModel(QAbstractListModel):
    label_role = Qt.UserRole + 1
    icon_role = Qt.UserRole + 2
    subitems_role = Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)

    def roleNames(self):
        return {
            self.label_role: b'label',
            self.icon_role: b'icon',
            self.subitems_role: b'subItems',
        }

    def rowCount(self, index):
        # return len(self.items)
        return mainmenu.model.count_get()

    def data(self, index, role):
        # print("***** data(%s, %s)" % (index.row(), role))
        if role == self.label_role:
            return mainmenu.model.data_get(index.row(), 'label')
        elif role == self.icon_role:
            return mainmenu.model.data_get(index.row(), 'icon')
        elif role == self.subitems_role:
            return mainmenu.model.data_get(index.row(), 'subitems')


class BrowserModel(QAbstractListModel):
    label_role = Qt.UserRole + 1
    icon_role = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)

    def roleNames(self):
        return {
            self.label_role: b'label',
            self.icon_role: b'icon'
        }

    def rowCount(self, index):
        # print("***** rowCount() -> %d" % len(self.items))
        return 1000

    def data(self, index, role):
        # print("***** data(%s, %s)" % (index.row(), role))
        # item = self.items[index.row()]
        # if role == self.label_role:
        if role == self.label_role:
            return 'Item #%d' % index.row()
        # elif role == self.icon_role:
        #     return item['icon']


class GuiCommunicator(QObject):

    @Slot(int)
    def mainmenu_item_selected(self, index):
        # TODO or we can use the model instead ??
        print("mainmenu_item_selected(%s)" % index)
        mainmenu.model.item_selected(index)

    @Slot(str, result=str)
    def i18n(self, string):
        return string + 'pippo'


class EmcGui(EmcGui_Base):
    """ PySide2 implementation of the EmcWindow """
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._qml_engine = None
        self._model1 = None
        self._model2 = None
        self._backend_instance = None

    def create(self) -> bool:
        # search the main QML file
        path = utils.get_resource('themes', self._theme_name, 'main.qml')
        if not path:
            ERR('Cannot find theme: "{}"'.format(self._theme_name))
            return False
        LOG('Loading theme: "{}"'.format(path))

        # create the QML engine
        self._qml_engine = QQmlApplicationEngine()

        # inject MainMenu and Browser model
        ctxt = self._qml_engine.rootContext()
        self._model1 = MainMenuModel()
        ctxt.setContextProperty('MainMenuModel', self._model1)
        self._model2 = BrowserModel()
        ctxt.setContextProperty('BrowserModel', self._model2)

        # inject the Communicator class
        self._backend_instance = b = GuiCommunicator()
        ctxt.setContextProperty("EmcBackend", b)

        # load and show the QML theme
        self._qml_engine.load(path)
        if not self._qml_engine.rootObjects():
            # TODO: find a decent way to detect load errors !!!!!!!!!!!!!!!!!!!!
            ERR('Cannot create the QML view')
            return False

        return True

    def destroy(self) -> None:
        del self._qml_engine
        del self._model1
        del self._model2

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

from nepymc.gui_base import EmcWindow_Base
from nepymc import utils

from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt, QAbstractListModel


def LOG(*args):
    print('GUI_QT:', *args)


def ERR(*args):
    print('GUI_QT ERROR:', *args, file=sys.stderr)


def DBG(*args):
    print('GUI_QT:', *args)
    pass


class MainMenuModel(QAbstractListModel):
    # TODO use QAbstractItemModel instead for tree ability ??
    label_role = Qt.UserRole + 1
    icon_role = Qt.UserRole + 2

    def __init__(self, parent=None):
        print("***** __init__")
        super().__init__(parent)
        self.items = [
            {'label': "UI tests", 'icon': 'star'},
            {'label': "Optical Discs", 'icon': 'optical'},
            {'label': "Musica", 'icon': 'music'},
            {'label': "Film", 'icon': 'movie'},
            {'label': "Serie TV", 'icon': 'tv'},
            {'label': "Canali Online", 'icon': 'olvideo'},
            {'label': "Photo", 'icon': 'photo'},
            {'label': "Settings", 'icon': 'config'},
            {'label': "Quit", 'icon': 'exit'},
        ]

    def roleNames(self):
        return {
            self.label_role: b'label',
            self.icon_role: b'icon'
        }

    def rowCount(self, index):
        print("***** rowCount() -> %d" % len(self.items))
        return len(self.items)

    def data(self, index, role):
        print("***** data(%s, %s)" % (index.row(), role))
        item = self.items[index.row()]
        if role == self.label_role:
            return item['label']
        elif role == self.icon_role:
            return item['icon']


class BrowserModel(QAbstractListModel):
    label_role = Qt.UserRole + 1
    icon_role = Qt.UserRole + 2

    def __init__(self, parent=None):
        print("***** __init__")
        super().__init__(parent)

    def roleNames(self):
        return {
            self.label_role: b'label',
            self.icon_role: b'icon'
        }

    def rowCount(self, index):
        # print("***** rowCount() -> %d" % len(self.items))
        print("***** rowCount() -> %d" % 1000)
        return 1000

    def data(self, index, role):
        print("***** data(%s, %s)" % (index.row(), role))
        # item = self.items[index.row()]
        # if role == self.label_role:
        if role == self.label_role:
            return 'Item #%d' % index.row()
        # elif role == self.icon_role:
        #     return item['icon']
        print("@"*80)


class EmcWindow(EmcWindow_Base):
    """ PySide2 implementation of the EmcWindow """
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._qml_engine = None
        self._model1 = None
        self._model2 = None

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

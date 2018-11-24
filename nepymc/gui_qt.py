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


from nepymc.gui_base import EmcWindow_Base
from nepymc import utils

from PySide2.QtQml import QQmlApplicationEngine


def LOG(*args):
    print('GUI_QT:', *args)


def ERR(*args):
    print('GUI_QT ERROR:', *args)


def DBG(*args):
    print('GUI_QT:', *args)
    pass


# from PySide2 import Qt
from PySide2 import QtCore


# class MainMenuModel(QtCore.QAbstractItemModel):
# def __init__(self, parent=None):
# super(MainMenuModel, self).__init__(parent)

class MainMenuModel(QtCore.QAbstractListModel):
    label_role = QtCore.Qt.UserRole + 1
    icon_role = QtCore.Qt.UserRole + 2

    def __init__(self, parent=None):
        print("***** __init__")
        super(MainMenuModel, self).__init__(parent)
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


class EmcWindow(EmcWindow_Base):
    """ PySide2 implementation of the EmcWindow """

    def create(self) -> bool:
        # search the main QML file
        path = utils.get_resource('themes', self._theme_name, 'main_window.qml')
        if not path:
            ERR('Cannot find the requested theme: "{}"'.format(
                self._theme_name))
            return False

        # create the QML engine
        self._engine = QQmlApplicationEngine()

        # inject MainMenu model
        ctxt = self._engine.rootContext()
        model = MainMenuModel()
        ctxt.setContextProperty('MainMenuModel', model)

        # load and show the QML theme
        self._engine.load(path)
        if not self._engine.rootObjects():
            # TODO: find a decent way to detect load errors !!!!!!!!!!!!!!!!!!!!
            ERR('Cannot create the QML view')
            return False

        return True

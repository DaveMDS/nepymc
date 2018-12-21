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

from nepymc import utils
from nepymc import mainmenu
from nepymc.gui_base import EmcGui_Base
from nepymc.model import EmcModelViewInterface


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
        return mainmenu.model.item_count_get()

    def data(self, index, role):
        # print("***** data(%s, %s)" % (index.row(), role))
        if role == self.label_role:
            return mainmenu.model.item_data_get(index.row(), 'label')
        elif role == self.icon_role:
            return mainmenu.model.item_data_get(index.row(), 'icon')
        elif role == self.subitems_role:
            return mainmenu.model.item_data_get(index.row(), 'subitems')


class BrowserModel(QAbstractListModel):
    label_role = Qt.UserRole + 1
    label_end_role = Qt.UserRole + 2
    icon_role = Qt.UserRole + 3
    icon_end_role = Qt.UserRole + 4
    info_role = Qt.UserRole + 5
    role_names_qt = {
        label_role: b'label',
        label_end_role: b'label_end',
        icon_role: b'icon',
        icon_end_role: b'icon_end',
        info_role: b'info',
    }
    role_names = {
        label_role: 'label',
        label_end_role: 'label_end',
        icon_role: 'icon',
        icon_end_role: 'icon_end',
        info_role: 'info',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._emc_model = None  # EmcModel to extract data from

    @property
    def emc_model(self):
        return self._emc_model

    @emc_model.setter
    def emc_model(self, model):
        self.beginResetModel()
        self._emc_model = model
        model.view_reset = self.model_hook_reset
        self.endResetModel()

    def item_selected(self, index):
        self._emc_model.item_selected(index)

    # Emc model hooks implementation
    def model_hook_reset(self):
        self.beginResetModel()
        self.endResetModel()

    # Qt model implementation (just a proxy to the emc model)
    def roleNames(self):
        return self.role_names_qt

    def rowCount(self, index):
        return self._emc_model.item_count_get() if self._emc_model else 0

    def data(self, index, role):
        if self._emc_model:
            return self._emc_model.item_data_get(index.row(), self.role_names[role])

    @Slot(int, str, result=str)
    def get(self, idx, role_name):
        """ Same as data, but to be used from QML """
        if self._emc_model:
            return self._emc_model.item_data_get(idx, role_name)


class GuiCommunicator(QObject):
    """ This is the EmcBackend object visible from QML """

    def __init__(self, gui):
        super().__init__()
        self._gui = gui

    @Slot(int)
    def mainmenu_item_selected(self, index):
        # TODO or we can use the model instead ??
        print("mainmenu_item_selected(%s)" % index)
        mainmenu.model.item_selected(index)

    @Slot(int)
    def browser_item_selected(self, index):
        # TODO or we can use the model instead ??
        print("browser_item_selected(%s)" % index)
        # mainmenu.model.item_selected(index)
        self._gui._browser_model_qt.item_selected(index)

    @Slot(str, result=str)
    def i18n(self, string):
        return string + 'pippo'

    @Slot(None, result=str)
    def application_name(self):
        # TODO questo dovrebbe essere una @property
        return "Not Emotion Media Center"


class EmcGui(EmcGui_Base):
    """ PySide2 implementation of the EmcWindow """
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._qml_engine = None
        self._model1 = None
        self._browser_model_qt = None
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
        self._browser_model_qt = BrowserModel()
        ctxt.setContextProperty('BrowserModel', self._browser_model_qt)

        # inject the Communicator class
        self._backend_instance = b = GuiCommunicator(self)
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
        del self._browser_model_qt

    def activate_section(self, section: str) -> None:
        root = self._qml_engine.rootObjects()[0]
        root.activate_section(section)

    def model_set(self, section: str, model: EmcModelViewInterface):
        if section == 'browser':
            # self._browser_model_qt.beginResetModel()
            self._browser_model_qt.emc_model = model
            # self._browser_model_qt.endResetModel()

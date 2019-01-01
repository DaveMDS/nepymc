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
import sys

from PySide2 import QtCore
from PySide2 import QtQml
from PySide2 import QtNetwork

from nepymc import utils
from nepymc import mainmenu
from nepymc.gui import EmcGui
from nepymc.model import EmcModelViewInterface


def LOG(*args):
    print('GUI_QT:', *args)


def ERR(*args):
    print('GUI_QT ERROR:', *args, file=sys.stderr)


def DBG(*args):
    print('GUI_QT:', *args)
    pass


class MainMenuModel(QtCore.QAbstractListModel):
    label_role = QtCore.Qt.UserRole + 1
    icon_role = QtCore.Qt.UserRole + 2
    subitems_role = QtCore.Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)

    # Qt model implementation (just a proxy to the mainmenu emc model)
    def roleNames(self):
        return {
            self.label_role: b'label',
            self.icon_role: b'icon',
            self.subitems_role: b'subItems',
        }

    def rowCount(self, index):
        return mainmenu.model.item_count_get()

    def data(self, index, role):
        # print("***** data(%s, %s)" % (index.row(), role))
        if role == self.label_role:
            return mainmenu.model.item_data_get(index.row(), 'label')
        elif role == self.icon_role:
            return mainmenu.model.item_data_get(index.row(), 'icon')
        elif role == self.subitems_role:
            return mainmenu.model.item_data_get(index.row(), 'subitems')

    # below methods are to be called from QML
    @QtCore.Slot(int)
    def item_selected(self, index):
        """ An in item has been selected in QML """
        print("mainmenu_item_selected(%s)" % index)
        mainmenu.model.item_selected(index)


class BrowserModel(QtCore.QAbstractListModel):
    label_role = QtCore.Qt.UserRole + 1
    label_end_role = QtCore.Qt.UserRole + 2
    icon_role = QtCore.Qt.UserRole + 3
    icon_end_role = QtCore.Qt.UserRole + 4
    info_role = QtCore.Qt.UserRole + 5
    poster_role = QtCore.Qt.UserRole + 6
    cover_role = QtCore.Qt.UserRole + 7
    role_names_qt = {
        label_role: b'label',
        label_end_role: b'label_end',
        icon_role: b'icon',
        icon_end_role: b'icon_end',
        info_role: b'info',
        poster_role: b'poster',
        cover_role: b'cover',
    }
    role_names = {
        label_role: 'label',
        label_end_role: 'label_end',
        icon_role: 'icon',
        icon_end_role: 'icon_end',
        info_role: 'info',
        poster_role: 'poster',
        cover_role: 'cover',
    }

    def __init__(self, gui, parent=None):
        super().__init__(parent)
        self._emc_model = None  # EmcModel to extract data from
        self._gui = gui

    @property
    def emc_model(self):
        return self._emc_model

    @emc_model.setter
    def emc_model(self, model):
        self.beginResetModel()
        self._emc_model = model
        model.view_reset = self.model_hook_reset
        model.select_item = self.model_hook_select_item
        self.endResetModel()

    # Emc model hooks implementation (called by the model)
    def model_hook_reset(self):
        self.beginResetModel()
        self.endResetModel()

    def model_hook_select_item(self, index):
        self._gui.page_item_select(index)

    # Qt model implementation (just a proxy to the emc model)
    def roleNames(self):
        return self.role_names_qt

    def rowCount(self, index):
        return self._emc_model.item_count_get() if self._emc_model else 0

    def data(self, index, role):
        if self._emc_model:
            return self._emc_model.item_data_get(index.row(), self.role_names[role])

    # below methods are to be called from QML
    @QtCore.Slot(int, str, result=str)
    def get(self, idx, role_name):
        """ Same as data, but to be used from QML """
        if self._emc_model:
            return self._emc_model.item_data_get(idx, role_name)

    @QtCore.Slot(int)
    def item_selected(self, index):
        """ An in item has been selected in QML """
        print("item_selected(%s)" % index)
        self._emc_model.item_selected(index)


class GuiCommunicator(QtCore.QObject):
    """ This is the EmcBackend object visible from QML """

    def __init__(self, gui):
        super().__init__()
        self._gui = gui

    # @Slot(int)
    # def mainmenu_item_selected(self, index):
    #     """ Called by QML to notify a mainmenu item has been selected """
    #     print("mainmenu_item_selected(%s)" % index)
    #     mainmenu.model.item_selected(index)

    @QtCore.Slot(str, result=str)
    def i18n(self, string):
        return string + 'pippo'

    @QtCore.Slot(None, result=str)
    def application_name(self):
        # TODO questo dovrebbe essere una @property
        return "Not Emotion Media Center"


class QMLNetworkDiskCache(QtNetwork.QAbstractNetworkCache):
    """ Provide on-file cache for all QML net requests """

    def metaData(self, qurl):
        """ Qt request a previously stored metadata for url """
        DBG('DiskCache: metaData() for "{}"'.format(qurl.url()))
        cache_path = utils.cache_path_for_url(qurl.url())
        meta = QtNetwork.QNetworkCacheMetaData()
        if os.path.exists(cache_path):
            meta.setUrl(qurl)
            # TODO !!!!
            meta.setExpirationDate(QtCore.QDateTime(2050, 1, 1, 0, 0, 0))
        return meta

    def prepare(self, metadata):
        """ Qt is going to download the resource, we need to provide a
            QIODevice opened for writing """
        DBG('DiskCache: prepare() for "{}"'.format(metadata.url().url()))
        if not metadata.isValid() or not metadata.url().isValid():
            return None

        cache_path = utils.cache_path_for_url(metadata.url().url())
        dirname = os.path.dirname(cache_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        f = QtCore.QFile(cache_path, self)  # parent=self to keep alive
        if f.open(QtCore.QIODevice.WriteOnly) is False:
            ERR('Cannot open "{}" for writing'.format(cache_path))
            return None
        else:
            return f

    def insert(self, device):
        """ Qt finish the download, we can close and delete the QIODevice we
            opened in the prepare method """
        device.close()
        device.deleteLater()
        del device

    def data(self, qurl):
        """ Qt request an opened file for reading the cached data from """
        DBG('DiskCache: data() for "{}"'.format(qurl.url()))
        path = utils.cache_path_for_url(qurl.url())
        f = QtCore.QFile(path, self)  # parent=self to keep alive
        if f.open(QtCore.QIODevice.ReadOnly) is False:
            ERR('Cannot open "{}" for reading'.format(path))
            return None
        else:
            return f


class QMLNetworkAccessManagerFactory(QtQml.QQmlNetworkAccessManagerFactory):
    """ Factory to build a NetworkAccessManager for QML net requests """
    def create(self, parent: QtCore.QObject):
        nam = QtNetwork.QNetworkAccessManager()
        disk_cache = QMLNetworkDiskCache(nam)
        nam.setCache(disk_cache)
        return nam


class EmcGui_Qt(EmcGui):
    """ PySide2 implementation of the EmcWindow """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._qml_engine = None
        self._qml_root = None
        self._model1 = None
        self._browser_model_qt = None
        self._backend_instance = None
        self._nam_factory = None

    def create(self) -> bool:
        # search the main QML file
        path = utils.get_resource('themes', self._theme_name, 'main.qml')
        if not path:
            ERR('Cannot find theme: "{}"'.format(self._theme_name))
            return False
        LOG('Loading theme: "{}"'.format(path))

        # create the QML engine
        self._qml_engine = QtQml.QQmlApplicationEngine()

        # inject MainMenu and Browser model
        ctxt = self._qml_engine.rootContext()
        self._model1 = MainMenuModel()
        ctxt.setContextProperty('MainMenuModel', self._model1)
        self._browser_model_qt = BrowserModel(self)
        ctxt.setContextProperty('BrowserModel', self._browser_model_qt)

        # inject the Communicator class
        self._backend_instance = GuiCommunicator(self)
        ctxt.setContextProperty('EmcBackend', self._backend_instance)

        # inject the network cache manager
        self._nam_factory = QMLNetworkAccessManagerFactory()
        self._qml_engine.setNetworkAccessManagerFactory(self._nam_factory)

        # load and show the QML theme
        self._qml_engine.load(path)
        roots = self._qml_engine.rootObjects()
        if not roots:
            ERR('Cannot create the QML view')
            return False

        # keep a reference of the main QML object for fast access
        self._qml_root = roots[0]

        return True

    def destroy(self) -> None:
        del self._qml_engine
        del self._model1
        del self._browser_model_qt

    def activate_section(self, section: str) -> None:
        self._qml_root.activate_section(section)

    def hide_section(self, section: str) -> None:
        self._qml_root.hide_section(section)

    def model_set(self, section: str, model: EmcModelViewInterface):
        if section == 'browser':
            # self._browser_model_qt.beginResetModel()
            self._browser_model_qt.emc_model = model
            # self._browser_model_qt.endResetModel()

    def page_title_set(self, title: str):
        self._qml_root.page_title_set(title)

    def page_icon_set(self, icon: str):
        self._qml_root.page_icon_set(icon)

    def page_item_select(self, index: int):
        self._qml_root.page_item_select(index)

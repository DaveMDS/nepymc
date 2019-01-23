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
from PySide2 import QtGui
from PySide2 import QtQml
from PySide2 import QtNetwork
from PySide2.QtCore import Qt

from nepymc import utils
from nepymc import mainmenu
from nepymc import input_events
from nepymc.gui import EmcGui
from nepymc.model import EmcModelViewInterface


def LOG(*args):
    print('GUI_QT:', *args)


def ERR(*args):
    print('GUI_QT ERROR:', *args, file=sys.stderr)


def DBG(*args):
    # print('GUI_QT:', *args)
    pass


DEFAULT_KEYS = {
    # Qt enum name => EMC event name
    'Key_Up': 'UP',
    'Key_Down': 'DOWN',
    'Key_Left': 'LEFT',
    'Key_Right': 'RIGHT',
    'Key_Enter': 'OK',
    'Key_Return': 'OK',
    'Key_Backspace': 'BACK',
    'Key_Escape': 'EXIT',

    'Key_Space': 'TOGGLE_PAUSE',
    'Key_MediaTogglePlayPause': 'TOGGLE_PAUSE',
    'Key_MediaPause': 'PAUSE',
    'Key_MediaPlay': 'PLAY',
    'Key_MediaStop': 'STOP',
    'Key_Plus': 'VOLUME_UP',
    'Key_Minus': 'VOLUME_DOWN',
    'Key_M': 'VOLUME_MUTE',
    'Key_P': 'TOGGLE_PAUSE',
    'Key_F': 'TOGGLE_FULLSCREEN',
    'Key_F1': 'VIEW_LIST',
    'Key_F2': 'VIEW_POSTERGRID',
    'Key_F3': 'VIEW_COVERGRID',
    'Key_F5': 'SCALE_SMALLER',
    'Key_F6': 'SCALE_BIGGER',
    'Key_F7': 'SCALE_RESET',
    'Key_S': 'STOP',
    'Key_Z': 'FAST_BACKWARD',
    'Key_X': 'BACKWARD',
    'Key_C': 'FORWARD',
    'Key_V': 'FAST_FORWARD',
    'Key_B': 'PLAYLIST_PREV',
    'Key_N': 'PLAYLIST_NEXT',
    'Key_Q': 'SUBS_DELAY_LESS',
    'Key_W': 'SUBS_DELAY_MORE',
    'Key_E': 'SUBS_DELAY_ZERO',
    'Key_D': 'TOGGLE_DVD_MENU',
}


INPUT_KEYS_MAP = {
    # EMC input event => Qt key (These are the only keys received in QML)
    'UP': Qt.Key_Up,
    'DOWN': Qt.Key_Down,
    'LEFT': Qt.Key_Left,
    'RIGHT': Qt.Key_Right,
    'OK': Qt.Key_Select,
    'BACK': Qt.Key_Back,
    'EXIT': Qt.Key_Exit,
}


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
        if role == self.label_role:
            return mainmenu.model.item_data_get(index.row(), 'label') or ''
        elif role == self.icon_role:
            return mainmenu.model.item_data_get(index.row(), 'icon') or ''
        elif role == self.subitems_role:
            return mainmenu.model.item_data_get(index.row(), 'subitems') or ''

    # below methods are to be called from QML
    @QtCore.Slot(int, int)
    def item_selected(self, index, subindex):
        """ An in item has been selected in QML """
        mainmenu.model.item_selected(index, subindex)


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

"""
class NavigatorProxyModel(QtCore.QAbstractListModel):
    label_role = QtCore.Qt.UserRole + 1
    label_end_role = QtCore.Qt.UserRole + 2
    icon_role = QtCore.Qt.UserRole + 3
    icon_end_role = QtCore.Qt.UserRole + 4
    info_role = QtCore.Qt.UserRole + 5
    poster_role = QtCore.Qt.UserRole + 6
    cover_role = QtCore.Qt.UserRole + 7
    role_names_qt = {
        label_role: b'title',  #  TODO rename roles based on EmcMediaItem ???
        label_end_role: b'label_end',
        icon_role: b'icon',
        icon_end_role: b'icon_end',
        info_role: b'info',
        poster_role: b'poster',
        cover_role: b'cover',
    }
    role_names = {
        label_role: 'title',
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
        # self.direction = 0

    @property
    def emc_model(self):
        return self._emc_model

    @emc_model.setter
    def emc_model(self, model):
        self.beginResetModel()
        self._emc_model = model
        # model.view_reset = self.model_hook_reset
        # model.select_item = self.model_hook_select_item
        self.endResetModel()

    # Qt model implementation (just a proxy to the emc model)
    def roleNames(self):
        return self.role_names_qt

    def rowCount(self, index):
        return self._emc_model.count_get() if self._emc_model else 0

    def data(self, index, role):
        if self._emc_model:
            item_data = self._emc_model.item_get(index.row())
            return item_data.get(self.role_names[role], '')
        return ''

    # below methods are to be called from QML
    @QtCore.Slot(int, str, result=str)
    def get(self, idx, role_name):
        "" Same as data, but to be used from QML scripts ""
        if self._emc_model:
            item = self._emc_model.item_get(idx)
            return item.get(role_name)

    @QtCore.Slot(int)
    def item_activated(self, idx):
        "" An in item has been activated in QML ""
        self._emc_model.item_activated(idx)

    @QtCore.Slot(result=int)
    def get_direction(self):
        "" TODO ""
        print("------------", self._emc_model.direction)
        return self._emc_model.direction
"""


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


class EventManager(QtCore.QObject):
    """
    This object receive ALL Qt events, filter out non keys events and forward
    pressed events to EMC.

    EMC will manage the event (keyb_module) and will fire the correct EMC
    input event based on user bindings.

    This object will then receive the EMC input event and forward it to QML as
    a standard qt key event.
    """
    def __init__(self, gui):
        super().__init__()
        self._gui = gui

        # listen to EMC input events
        input_events.listener_add('qt-gui', self.emc_input_event)

    def eventFilter(self, obj, qt_event):
        """ Qt keys events => EMC events """

        if qt_event.type() != QtCore.QEvent.KeyPress:
            return False  # not a key event, let Qt manage it

        if not qt_event.spontaneous():
            return False  # we generate this event, let it goes to QML

        # this keyb event comes from the window, forward it to EMC by name
        key = Qt.Key(qt_event.key())
        self._gui.key_down_send(key.name.decode())
        return True  # stop propagation

    def emc_input_event(self, emc_event):
        """ EMC input events => Qt key event """
        qt_key = INPUT_KEYS_MAP.get(emc_event)
        if qt_key:
            ev = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, qt_key, Qt.NoModifier)
            QtGui.QGuiApplication.sendEvent(self._gui._qml_root, ev)
            if ev.isAccepted():
                return input_events.EVENT_BLOCK
            else:
                return input_events.EVENT_CONTINUE
        else:
            DBG("Unknow EMC event:", emc_event)
            return input_events.EVENT_CONTINUE


class EmcGui_Qt(EmcGui):
    """ PySide2 implementation of the EmcWindow """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._qml_engine = None
        self._qml_root = None
        self._model1 = None
        self._browser_model_qt = None
        # self._navigator_proxymodel = NavigatorProxyModel(self)
        self._backend_instance = None
        self._nam_factory = None
        self._events_manager = None

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

        # ctxt.setContextProperty('NavigatorModel', self._navigator_proxymodel)

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

        # all the keyboard input must be forwarded to EMC and ignored
        self._events_manager = EventManager(self)
        QtGui.QGuiApplication.instance().installEventFilter(self._events_manager)

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
        # elif section == 'navigator':
        #     self._navigator_proxymodel.emc_model = model

    def page_title_set(self, title: str):
        self._qml_root.page_title_set(title)

    def page_icon_set(self, icon: str):
        self._qml_root.page_icon_set(icon)

    def page_item_select(self, index: int):
        self._qml_root.page_item_select(index)

    def default_keymap_get(self):
        return DEFAULT_KEYS

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

from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt, QObject, Slot, QAbstractListModel

from nepymc import utils
from nepymc import mainmenu
from nepymc.gui_base import EmcGui_Base, EmcDialog_Base
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
    @Slot(int)
    def item_selected(self, index):
        """ An in item has been selected in QML """
        print("mainmenu_item_selected(%s)" % index)
        mainmenu.model.item_selected(index)


class BrowserModel(QAbstractListModel):
    label_role = Qt.UserRole + 1
    label_end_role = Qt.UserRole + 2
    icon_role = Qt.UserRole + 3
    icon_end_role = Qt.UserRole + 4
    info_role = Qt.UserRole + 5
    poster_role = Qt.UserRole + 6
    cover_role = Qt.UserRole + 7
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
    @Slot(int, str, result=str)
    def get(self, idx, role_name):
        """ Same as data, but to be used from QML """
        if self._emc_model:
            return self._emc_model.item_data_get(idx, role_name)

    @Slot(int)
    def item_selected(self, index):
        """ An in item has been selected in QML """
        print("item_selected(%s)" % index)
        self._emc_model.item_selected(index)


class GuiCommunicator(QObject):
    """ This is the EmcBackend object visible from QML """

    def __init__(self, gui):
        super().__init__()
        self._gui = gui

    # @Slot(int)
    # def mainmenu_item_selected(self, index):
    #     """ Called by QML to notify a mainmenu item has been selected """
    #     print("mainmenu_item_selected(%s)" % index)
    #     mainmenu.model.item_selected(index)

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
        self._qml_root = None
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
        self._browser_model_qt = BrowserModel(self)
        ctxt.setContextProperty('BrowserModel', self._browser_model_qt)

        # inject the Communicator class
        self._backend_instance = b = GuiCommunicator(self)
        ctxt.setContextProperty("EmcBackend", b)

        # load and show the QML theme
        self._qml_engine.load(path)
        roots = self._qml_engine.rootObjects()
        if not roots:
            ERR('Cannot create the QML view')
            return False

        # keep a reference of the main QML object
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

    def build_dialog(self, *args, **kargs) -> EmcDialog_Base:
        return EmcDialog(self, *args, **kargs)


class EmcDialog(EmcDialog_Base):
    """ PySide2 implementation of the EmcDialog """

    # dialogs_counter = 0

    def __init__(self, gui, title=None, text=None, content=None, spinner=False,
                 style='panel', done_cb=None, canc_cb=None, user_data=None):
        super().__init__(title, text, content, spinner, style,
                         done_cb, canc_cb, user_data)

        self._buttons = []
        self._gui = gui
        self._qml_obj = gui._qml_root.build_dialog(title, style, text,
                                                   content, spinner)

        # EmcDialog.dialogs_counter += 1
        # self._name = 'Dialog-' + str(EmcDialog.dialogs_counter)

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
        print("DEL")
        # del self._qml_obj
        self._qml_obj.emcDestroy()

    def main_content_set(self, content) -> None:
        raise NotImplementedError

    def button_add(self, label: str, selected_cb: callable = None,
                   cb_data: Any = None, icon: str = None,
                   default: bool = False) -> None:

        def button_clicked_cb(idx):
            b = self._buttons[idx]
            b['cb'](b['data'])

        newidx = len(self._buttons)
        btn = self._qml_obj.action_add(newidx, label, icon)
        btn.emcButtonClicked.connect(button_clicked_cb)
        self._buttons.append({'btn': btn, 'cb': selected_cb, 'data': cb_data})

    def buttons_clear(self):
        raise NotImplementedError

    def title_set(self, text: str):
        raise NotImplementedError

    def text_set(self, text: str):
        raise NotImplementedError

    def text_append(self, text: str) -> None:
        raise NotImplementedError

    def list_item_append(self, label: str, icon: str = None, end: str = None,
                         *args, **kwargs):
        raise NotImplementedError

    def list_clear(self):
        raise NotImplementedError

    def list_item_selected_get(self):
        raise NotImplementedError

    def list_item_icon_set(self, it, icon, end=False):
        raise NotImplementedError

    def spinner_start(self):
        raise NotImplementedError

    def spinner_stop(self):
        raise NotImplementedError

    def progress_set(self, val: float):
        raise NotImplementedError

    def autoscroll_enable(self, speed_scale: float = 1.0,
                          start_delay: float = 3.0):
        raise NotImplementedError




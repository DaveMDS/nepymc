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

from typing import Any, Optional
from abc import abstractmethod

from nepymc.utils import EmcBackendableABC


class EmcDialogListItem(object):
    def __init__(self, label, icon, end, args, kargs):
        self.label = label
        self.icon = icon
        self.end = end
        self.args = args
        self.kargs = kargs
        self.data = {}  # dict free for user


class EmcDialog(EmcBackendableABC):
    """
      style can be 'panel' or 'minimal'

      you can also apply special style that perform specific task:
         'info', 'error', 'warning', 'yesno', 'cancel', 'progress',
         'list', 'image_list_landscape', 'image_list_portrait',
         'buffering'
    """
    backendable_pkg = 'gui'
    backendable_cls = 'EmcDialog'

    # minimal_styles = ['info', 'error', 'warning', 'yesno', 'cancel', 'progress']
    list_styles = ['list', 'image_list_landscape', 'image_list_portrait']

    @abstractmethod
    def __init__(self, title: str=None, text: str=None,
                 content=None,  # TODO type ??
                 spinner: bool=False, style: str='panel',
                 done_cb: callable=None, canc_cb: callable=None,
                 user_data: Any=None):
        self._title = title
        self._text = text
        self._content = content
        self._spinner = spinner
        self._style = style
        self._done_cb = done_cb
        self._canc_cb = canc_cb
        self._user_data = user_data

        if style in ('image_list', 'image_list_horiz', 'image_list_vert'):
            raise RuntimeError('EmcDialog: DEPRECATED style')

    @abstractmethod
    def delete(self) -> None:
        """ TODOC """

    @abstractmethod
    def button_add(self, label: str,
                   selected_cb: callable = None, cb_data: Any = None,
                   icon: str = None, default: bool = False) -> None:
        """ TODOC """

    @abstractmethod
    def buttons_clear(self):
        """ TODOC """

    @abstractmethod
    def content_set(self, content: Optional[str]) -> None:
        """ set the big image, content must be a valid image file """
        self._content = content

    @abstractmethod
    def title_set(self, title: str):
        """ TODOC """
        self._title = title

    @abstractmethod
    def text_set(self, text: str):
        """ TODOC """
        self._text = text

    @abstractmethod
    def text_append(self, text: str) -> None:
        """ TODOC """
        self._text += text

    @abstractmethod
    def list_item_append(self, label: str, icon: str=None, end: str=None,
                         *args, **kargs) -> EmcDialogListItem:
        """ TODOC """

    @abstractmethod
    def list_go(self):
        """ TODOC """

    @abstractmethod
    def list_clear(self):
        """ TODOC """

    @abstractmethod
    def list_item_selected_get(self) -> EmcDialogListItem:
        """ return the current selected item """

    @abstractmethod
    def list_item_icon_set(self, it, icon, end=False):  # TODO item type ?
        """ TODOC """

    @abstractmethod
    def spinner_start(self):
        """ TODOC """

    @abstractmethod
    def spinner_stop(self):
        """ TODOC """

    @abstractmethod
    def progress_set(self, val: float):
        """ TODOC """

    @abstractmethod
    def autoscroll_enable(self, speed_scale: float=1.0, start_delay: float=3.0):
        """ TODOC """

    def title_get(self):
        return self._title

    def content_get(self):
        # return self._content
        raise RuntimeError("EmcDialog: content_get() is no more")

    def data_get(self):
        return self._user_data

    def text_get(self):
        return self._text

    def _call_user_done_callback(self, selected_item: EmcDialogListItem=None):
        """  Utility for backends """
        # This code was only for the list dialogs....
        if self._done_cb:
            if selected_item:
                self._done_cb(self, *selected_item.args, **selected_item.kargs)
            # args, kwargs = it.data['_user_item_data_']
            # self._done_cb(self, *args, **kwargs)
        else:
            self.delete()


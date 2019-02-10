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

from abc import abstractmethod
from typing import Callable, Optional

from nepymc.utils import EmcBackendableABC, EmcObject
from nepymc.model import EmcModelViewInterface
from nepymc.mainloop import EmcMainLoop


def LOG(*args):
    print('GUI_BASE:', *args)


def DBG(*args):
    print('GUI_BASE:', *args)
    pass


class EmcGui(EmcObject, EmcBackendableABC):

    backendable_pkg = 'gui'
    backendable_cls = 'EmcGui'

    def __init__(self, mainloop: EmcMainLoop, theme_name: str):
        super().__init__(mainloop)  # mainloop is the gui parent
        self._mainloop = mainloop
        self._theme_name = theme_name
        self._key_down_func = None

    @abstractmethod
    def create(self) -> bool:
        return False

    @abstractmethod
    def activate_section(self, section: str) -> None:
        """ sections: mainmenu,browser """

    @abstractmethod
    def hide_section(self, section: str) -> None:
        """ sections: mainmenu,browser """

    @abstractmethod
    def model_set(self, section: str, model: EmcModelViewInterface) -> None:
        """ Set the EMC model for the given section """

    @abstractmethod
    def page_title_set(self, title: str) -> None:
        """ Set the page title """

    @abstractmethod
    def page_icon_set(self, icon: str) -> None:
        """ Set the page icon """

    @abstractmethod
    def default_keymap_get(self) -> None:
        """ Get the default keyboard mapping,
            key: 'backend_key_name' => 'EMC_EVENT'
        """

    @abstractmethod
    def volume_set(self, volume: float) -> None:
        """ Set the linear volume in the gui (0-100). For sliders,
            see VideoPlayer / AudioPlayer for logarithimc adjusted volume
        """

    #
    #  Utils for implementators
    #

    @staticmethod
    def volume_change_request(val: float) -> None:
        """ The gui request a new volume value (Linear 0-100)
            This usually comes from a slider changed by user
        """
        from nepymc import mediaplayer
        mediaplayer.volume_set(val)

    def key_down_connect(self, func: Optional[Callable[[str], None]]) -> None:
        """ Set a callback to be fired on each key stroke received
            This will be called by the keyb module, so it will receive
            backend key events. None to unset the callback.
        """
        self._key_down_func = func

    def key_down_send(self, key: str) -> None:
        """ Send the received keyboard events to EMC
            Backends must call this on each key press received from the win
        """
        if callable(self._key_down_func):
            self._key_down_func(key)

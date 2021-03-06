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

from nepymc.utils import EmcObject, EmcBackendableABC, Singleton
from nepymc.model import EmcModelViewInterface
from nepymc.mainloop import EmcMainLoop, EmcTimer
from nepymc import input_events
from nepymc import ini


def LOG(*args):
    print('GUI_BASE:', *args)


def DBG(*args):
    print('GUI_BASE:', *args)
    pass


class EmcGui(EmcObject, EmcBackendableABC, metaclass=Singleton):

    backendable_pkg = 'gui'
    backendable_cls = 'EmcGui'

    def __init__(self):
        super().__init__(EmcMainLoop.instance())  # mainloop is the gui parent

        # setup default ini values
        ini.set_default('general', 'theme', 'blackmirror')
        ini.set_default('general', 'fps', 30)
        ini.set_default('general', 'scale', 1.0)
        ini.set_default('general', 'fullscreen', False)
        ini.set_default('general', 'hide_mouse', False)
        ini.set_default('general', 'time_format', '%H:%M')
        ini.set_default('general', 'date_format', '%A %d %B')
        ini.set_default('general', 'keyb_layouts', 'en_abc symbols')

        # public members
        self._theme_name = ini.get('general', 'theme')

        # protected memebrs
        self._boot_in_fullscreen = ini.get_bool('general', 'fullscreen')

        # private members
        self._key_down_func = None
        self._mouse_hide_timer = EmcTimer(3.0, self._mouse_hide_timer_cb,
                                          parent=self)

        # listen for input events
        input_events.listener_add('EmcGuiBase', self._input_events_cb)

    #
    #  Methods that must be implemented by backends
    #

    @abstractmethod
    def delete(self):
        super().delete()
        input_events.listener_del('EmcGuiBase')

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

    @abstractmethod
    def backdrop_set(self, image: str) -> None:
        """ Change the background image of the whole UI """

    @abstractmethod
    def fullscreen_get(self) -> bool:
        """ Get the fullscreen status of the main window """

    @abstractmethod
    def fullscreen_set(self, fullscreen: bool) -> None:
        """ Change the fullscreen status of the main window """

    @abstractmethod
    def mouse_cursor_hidden_set(self, hide: bool) -> None:
        """ Change the mouse cursor hidden state on the main window """

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

    def mouse_move_event(self) -> None:
        """ This MUST be called by backend implementation on every mouse
            move event, it is used to manage the automatic mouse
            show/hide feature
        """
        self._mouse_hide_timer.reset()
        self.mouse_cursor_hidden_set(False)

    #
    #  Private
    #

    def _mouse_hide_timer_cb(self):
        if ini.get_bool('general', 'hide_mouse'):
            self.mouse_cursor_hidden_set(True)

    def _input_events_cb(self, event):
        if event == 'TOGGLE_FULLSCREEN':
            self.fullscreen_set(not self.fullscreen_get())
            return input_events.EVENT_BLOCK

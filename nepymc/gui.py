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

from nepymc import ini
from nepymc.model import EmcModelViewInterface
# from nepymc.mainloop_base import EmcMainLoop_Base


def LOG(*args):
    print('GUI:', *args)


def DBG(*args):
    print('GUI:', *args)
    pass


def ERR(*args):
    print('GUI ERROR:', *args, file=sys.stderr)


# from nepymc import gui_qt as gui  # TODO factorize !!!
from nepymc.gui_qt import EmcGui  # TODO factorize !!!

_backend_gui = None


def init(backend: str, loop) -> bool:   # TODO remove loop !!!!!!
    """ return: False=failed True=ok """
    global _backend_gui

    # get config values, setting defaults if needed
    theme = ini.get('general', 'theme', 'blackmirror')
    ini.get('general', 'gui_engine', 'qt')
    ini.get('general', 'fps', 30)
    ini.get('general', 'scale', 1.0)
    ini.get('general', 'fullscreen', False)
    ini.get('general', 'hide_mouse', False)
    ini.get('general', 'time_format', '%H:%M')
    ini.get('general', 'date_format', '%A %d %B')
    ini.get('general', 'keyb_layouts', 'en_abc symbols')

    _backend_gui = EmcGui(loop, theme)
    return _backend_gui.create()


def shutdown():
    global _backend_gui

    _backend_gui.destroy()
    del _backend_gui
    _backend_gui = None


def background_set(image: str) -> None:
    # global _backdrop_curr

    # if image == _backdrop_curr.file[0]:
    #    return
    #
    # if _backdrop_curr == _backdrop_im1:
    #    _backdrop_curr = _backdrop_im2
    #    signal = 'backdrop,show,2'
    # else:
    #    _backdrop_curr = _backdrop_im1
    #    signal = 'backdrop,show,1'
    #
    # try:
    #    _backdrop_curr.file_set(image)
    #    signal_emit(signal)
    # except: pass
    DBG("background_set", image)


def activate_section(section: str) -> None:
    _backend_gui.activate_section(section)


def hide_section(section: str) -> None:
    _backend_gui.hide_section(section)


def model_set(section: str, model: EmcModelViewInterface):
    _backend_gui.model_set(section, model)


def page_title_set(title: str) -> None:
    _backend_gui.page_title_set(title)


def page_icon_set(icon: str) -> None:
    _backend_gui.page_icon_set(icon)

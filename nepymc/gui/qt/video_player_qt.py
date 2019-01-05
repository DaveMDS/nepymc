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

# from PySide2.QtCore import Qt, QObject, Slot, QAbstractListModel

from nepymc import gui
from nepymc.gui import EmcVideoPlayer


def LOG(*args):
    print('VP_QT:', *args)


def ERR(*args):
    print('VP_QT ERROR:', *args, file=sys.stderr)


def DBG(*args):
    print('VP_QT:', *args)
    pass


class EmcVideoPlayer_Qt(EmcVideoPlayer):

    def __init__(self, url: str=None):
        super().__init__(url)
        print("INIT VIDEO PLAYER QT")

        self._gui = gui.instance()
        self._qml_obj = self._gui._qml_root.build_video_player(url)

    def delete(self) -> None:
        self._qml_obj.emcDestroy()

    def title_set(self, title: str) -> None:
        self._qml_obj.setProperty('title', title)

    def poster_set(self, poster: str) -> None:
        self._qml_obj.setProperty('poster', poster)

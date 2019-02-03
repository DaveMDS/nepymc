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

    def __init__(self):
        super().__init__()
        print("INIT VIDEO PLAYER QT")

        self._gui = gui.instance()
        self._qml_obj = self._gui._qml_root.activate_section('videoplayer')

    def delete(self) -> None:
        # self._qml_obj.emcDestroy()  # TODO call close() in qml??
        pass

    @property
    def url(self) -> str:
        return self._qml_obj.property('url')

    @url.setter
    def url(self, url: str) -> None:
        self._qml_obj.setProperty('url', url)

    @property
    def position(self) -> int:
        """ millis """
        return self._qml_obj.property('position')

    @position.setter
    def position(self, val: int):
        self._qml_obj.seek(val)

    @property
    def duration(self) -> int:
        """ millis """
        return self._qml_obj.property('duration')

    def volume_set(self, val: float) -> None:
        self._qml_obj.setProperty('volume', val / 100.0)

    def play(self) -> None:
        # make sure the videplayer is visible and focused
        self._gui._qml_root.activate_section('videoplayer')
        self._qml_obj.play()

    def pause(self) -> None:
        self._qml_obj.pause()

    def stop(self) -> None:
        self._qml_obj.stop()

    def title_set(self, title: str) -> None:
        self._qml_obj.setProperty('title', title)

    def poster_set(self, poster: str) -> None:
        self._qml_obj.setProperty('poster', poster)

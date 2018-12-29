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

from PySide2.QtCore import QTimer

from nepymc.mainloop import EmcTimer


class EmcTimer_Qt(EmcTimer):
    """ PySide2 implementation of the EmcTimer """

    def __init__(self, interval: int, callback: callable,
                 oneshot: bool=False, onstart: bool=False, **kargs):
        super().__init__(interval, callback, oneshot, onstart, **kargs)

        self._timer = QTimer()
        self._timer.timeout.connect(self._call_user_callback)
        self._timer.setInterval(1000)
        self._timer.start()

    def delete(self) -> None:
        if self._timer:
            self._timer.stop()
            del self._timer
            self._timer = None
        del self

    def start(self) -> None:
        if self._timer:
            self._timer.start()

    def stop(self) -> None:
        if self._timer:
            self._timer.stop()

    def reset(self) -> None:
        if self._timer:
            self._timer.setInterval(self._interval)

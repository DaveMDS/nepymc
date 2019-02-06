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

from PySide2.QtCore import QAbstractAnimation

from nepymc.mainloop import EmcIdler


class EmcIdler_Qt(EmcIdler):
    """ PySide2 implementation of the EmcIdler """

    def __init__(self, callback: callable, oneshot: bool = False, **kargs):
        super().__init__(callback, oneshot, **kargs)

        self._animator = Animator(self)
        self._animator.start()

    def delete(self) -> None:
        if self._animator:
            self._animator.stop()
            del self._animator
            self._animator = None
        del self

    def pause(self) -> None:
        if self._animator:
            self._animator.pause()

    def resume(self) -> None:
        if self._animator:
            self._animator.resume()

    # expose this "private" method for usage within the Animator class
    call_user_callback = EmcIdler._call_user_callback


class Animator(QAbstractAnimation):
    def __init__(self, idler):
        super().__init__()
        self._idler = idler

    def duration(self):
        return -1

    def updateCurrentTime(self, time: int):
        self._idler.call_user_callback()

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

from nepymc.utils import EmcBackendableABC
from nepymc.mainloop import EmcTimer


class EmcNotify(EmcBackendableABC):
    """  TODOC """
    backendable_pkg = 'gui'
    backendable_cls = 'EmcNotify'

    @abstractmethod
    def __init__(self, text, image='icon/star', hidein=5.0, close_cb=None):
        self.text = text
        self.image = image
        self._close_cb = close_cb
        self._timer = None
        if hidein:
            self.hidein(hidein)

    @abstractmethod
    def delete(self):
        if self._timer:
            self._timer.delete()

    def hidein(self, hidein):
        if self._timer:
            self._timer.delete()
        self._timer = EmcTimer(int(hidein * 1000), self._hide_timer_cb)

    def _hide_timer_cb(self):
        self.delete()
    #     if callable(self.close_cb):
    #         self.close_cb()

    @abstractmethod
    def text_set(self, text):
        self.text = text

    @abstractmethod
    def image_set(self, image):
        self.image = image


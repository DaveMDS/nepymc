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
from typing import Optional

from nepymc.utils import EmcBackendableABC, EmcObject
from nepymc.mainloop import EmcTimer


class EmcNotify(EmcObject, EmcBackendableABC):
    """  TODOC """
    backendable_pkg = 'gui'
    backendable_cls = 'EmcNotify'

    @abstractmethod
    def __init__(self, text: str, image: str = 'icon/star',
                 hidein: float = 5.0, parent: Optional[EmcObject] = None):
        super().__init__(parent)
        self.text = text
        self.image = image
        self._timer = None
        if hidein:
            self.hidein(hidein)

    def hidein(self, hidein):
        self._timer = EmcTimer(int(hidein * 1000), self._hide_timer_cb,
                               parent=self)

    def _hide_timer_cb(self):
        self.delete()

    @abstractmethod
    def text_set(self, text):
        self.text = text

    @abstractmethod
    def image_set(self, image):
        self.image = image


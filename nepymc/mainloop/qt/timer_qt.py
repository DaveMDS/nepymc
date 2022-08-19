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

from PySide6.QtCore import QTimer

from nepymc.mainloop import EmcTimer
from nepymc.utils import EmcObject


class EmcTimer_Qt(EmcTimer):
    """ PySide2 implementation of the EmcTimer """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self._timer = QTimer()
        self._timer.timeout.connect(self._call_user_callback)
        self._timer.setInterval(int(self._interval * 1000))
        self._timer.start()

    def delete(self) -> None:
        super().delete()
        if self._timer:
            self._timer.stop()
            self._timer = None

    def start(self) -> None:
        if not self.deleted:
            self._timer.start()

    def stop(self) -> None:
        if not self.deleted:
            self._timer.stop()

    def reset(self) -> None:
        if not self.deleted:
            self._timer.start()

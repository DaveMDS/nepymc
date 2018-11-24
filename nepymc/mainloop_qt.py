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

from PySide2.QtGui import QGuiApplication

from nepymc.mainloop_base import EmcMainLoop_Base


def LOG(*args):
    print('MAINLOOP:', *args)


def DBG(*args):
    print('MAINLOOP:', *args)
    pass


class EmcMainLoop(EmcMainLoop_Base):
    """ PySide2 implementation of the EmcMainLoop """

    def __init__(self):
        self._app = QGuiApplication(sys.argv)

    def run(self):
        DBG('run()')
        self._app.exec_()

    def exit(self):
        self._app.quit()

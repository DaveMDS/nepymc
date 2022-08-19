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

from PySide6.QtCore import QProcess

from nepymc.mainloop import EmcExe


class EmcExe_Qt(EmcExe):
    """ PySide2 implementation of the EmcExec """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self._proc = QProcess()
        self._proc.errorOccurred.connect(self._error_cb)

        if self._done_cb:
            self._proc.finished.connect(self._finished_cb)

        if self._grab_output:
            self._proc.readyReadStandardOutput.connect(self._stdout_cb)

        if self._params:
            self._proc.start(self._cmd, self._params)
        else:
            self._proc.start(self._cmd)

    def delete(self) -> None:
        super().delete()
        if self._proc and self._proc.state() == QProcess.Running:
            self._proc.kill()
        self._proc = None

    def _finished_cb(self, exit_code):
        self._call_user_callback(exit_code)

    def _error_cb(self, error):
        if self._proc and not self.deleted:
            self._call_user_callback(-1)

    def _stdout_cb(self):
        if self._proc and not self.deleted:
            self._out_buffer.append(self._proc.readAllStandardOutput().data())

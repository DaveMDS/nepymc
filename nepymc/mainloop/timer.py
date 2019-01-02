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


class EmcTimer(EmcBackendableABC):
    """ TODOC """

    backendable_pkg = 'mainloop'
    backendable_cls = 'EmcTimer'

    @abstractmethod
    def __init__(self, interval: int, callback: callable=None,
                 oneshot: bool=False, onstart: bool=False, **kargs):
        """
        Params:
            interval: milliseconds between each call
            callback: user function to call when timer expire
            oneshot: Call just one time and then autodelete
            onstart: whenever to trigger the callback on start
            **kargs: any other keyword arguments will be passed back in callback
        """
        self._interval = interval
        self._callback = callback
        self._oneshot = oneshot
        self._onstart = onstart
        self._cb_kargs = kargs
        if onstart:
            self._call_user_callback()
        # try to catch old (deprecated) call in seconds
        if interval < 200 or isinstance(interval, float):
            raise RuntimeError('EmcTimer: milliseconds !!!!')

    @abstractmethod
    def delete(self) -> None:
        """ TODOC """

    @abstractmethod
    def start(self) -> None:
        """ TODOC """

    @abstractmethod
    def stop(self) -> None:
        """ TODOC """

    @abstractmethod
    def reset(self) -> None:
        """ TODOC """

    def _call_user_callback(self):
        if callable(self._callback):
            self._callback(**self._cb_kargs)
        if self._oneshot:
            self.delete()

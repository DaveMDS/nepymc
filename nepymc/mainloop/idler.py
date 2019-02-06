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


class EmcIdler(EmcBackendableABC):
    """ TODOC """

    backendable_pkg = 'mainloop'
    backendable_cls = 'EmcIdler'

    @abstractmethod
    def __init__(self, callback: callable, oneshot: bool=False, **kargs):
        """
        Params:
            callback: user function to call when the mainloop is idle
            oneshot: Call just one time and then autodelete
            **kargs: any other keyword arguments will be passed back in callback
        """
        self._callback = callback
        self._oneshot = oneshot
        self._cb_kargs = kargs

    @abstractmethod
    def delete(self) -> None:
        """ Stop the idler and free internal resource,
            no more methods can be used after this call
        """

    @abstractmethod
    def pause(self) -> None:
        """ Pause the idler, no more callback will be called """

    @abstractmethod
    def resume(self) -> None:
        """ Unpause the idler """

    def _call_user_callback(self):
        if callable(self._callback):
            self._callback(**self._cb_kargs)
        if self._oneshot:
            self.delete()

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
from typing import Iterable, Callable, Optional

from nepymc.utils import EmcBackendableABC


class EmcExec(EmcBackendableABC):
    """ Execute external command in async way """

    backendable_pkg = 'mainloop'
    backendable_cls = 'EmcExec'

    @abstractmethod
    def __init__(self, cmd: str, params: Iterable[str]=None,
                 grab_output: bool=False, decode: Optional[str]='utf8',
                 done_cb: Callable=None, **kargs):
        """
        Params:
            cmd (str): the command to run
            params (iterable[str]): parameters for the command
            grab_output: whenever to collect the stdoutput
            decode: how to decode the received bytes, can be:
                None: no decoding will be performed, you will get a bytearray
                'utf8': (the default) will decode to str
            done_cb: function to call when the program ends.
            **kargs: any other keywords arguments will be passed back in done_cb

        Callback signatures:
            done_cb(exit_code, outbuffer, **kargs)
                exit_code (int): will contain the exit code from the command
                out_buffer: will contain the standard output of the command or
                    an empty string if grab_input is False (the default)
                    The type of outbuffer depend on the decode argument
                **kargs are the ones passed in constructor
        """
        self._cmd = cmd
        self._params = params
        self._grab_output = grab_output
        self._decode = decode
        self._done_cb = done_cb
        self._cb_kargs = kargs
        # backend will fill this bytearray list with chunks received on stdout
        self._out_buffer = []

    @abstractmethod
    def delete(self) -> None:
        """ TODOC """
        del self  # not really sure about this :/

    def _call_user_callback(self, exit_code):
        if callable(self._done_cb):
            out = ''
            if self._grab_output:
                if self._decode == 'utf8':
                    out = b''.join(self._out_buffer).decode('utf8')
                elif self._decode is None:
                    out = b''.join(self._out_buffer)
                else:
                    raise RuntimeError('EmcExec: invalid decode method: {}'
                                       .format(repr(self._decode)))
            self._done_cb(exit_code, out, **self._cb_kargs)
        self.delete()

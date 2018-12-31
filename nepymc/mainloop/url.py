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

import os
import tempfile
from abc import abstractmethod
from urllib.parse import quote as urllib_quote
from typing import Optional

from nepymc.utils import EmcBackendableABC


class EmcUrl(EmcBackendableABC):
    """ Async fetch a remote url content in memory or to file

    A class to async retrive an url content.
    The download will automatically start on class instantiation.
    The downloaded data (bytes) will be converted to str using utf8 encoding.

    Properties:
        url (str): the url being downloaded
        dest (str): the resolved destination file, or '::mem::'

    Args:
        url (str): the url to retrive
        dest (str): If set to a local file name then the download data will be
            written to that file (created and overwritten if necessary, also the
            necessary parent directories are created).
            If dest is omitted (or is '::mem::') than the data will be only be
            saved to a mem buffer and returned as a dest param in the done cb.
            If dest '::tmp::' than the data will be written to a random created
            new temp file.
        done_cb (callable): function to call when the operation is completed
        prog_cb (callable): function to call while the operation is in progress
        min_size (int): if min_size is set (and > 0) than downloaded files
            smaller than this value (in bytes) will be discarted.
        headers (dict): additional headers for the request, fe:
            {'User-Agent': 'my user agent', ...}
        urlencode (bool): encode the given url (default to True).
        decode (str): How to decode received data (only valid for ::mem:: dest)
            Different decoding will result in different data type returned:
                None or '': No decoding will take place (type: bytes)
                'utf8': UTF-8 decode (type: str) This is the default.
                'json': TODO (type: object)
        **args: any other arguments will be passed back in the callbacks
        **kargs: any other karguments will be passed back in the callbacks

    Callback signatures:
        done_cb(url: EmcUrl, success: bool, dest: str or bytes, *args, **kargs)
            dest is the destination file name (str) in case of download to disk,
            or the data received in case of memory download (type in this case
            depend on the decode param passed at init).
        prog_cb(url: EmcUrl, total: int, received: int, *args, **kargs)

    """

    backendable_pkg = 'mainloop'
    backendable_cls = 'EmcUrl'

    @abstractmethod
    def __init__(self, url: str, dest: str='::mem::',
                 done_cb: callable=None, prog_cb: callable=None,
                 min_size: int=0, headers: dict=None, urlencode: bool=True,
                 decode: Optional[str]='utf8', *args, **kargs):

        # urlencode the url (but not the http:// part, or ':' will be converted)
        if urlencode:
            (_prot, _url) = url.split('://', 1)
            url = '://'.join((_prot, urllib_quote(_url)))

        # special destinations (:mem: and :tmp:)
        if not dest or dest == '::mem::':
            pass
        elif dest == '::tmp::':
            dest = tempfile.mktemp()
        elif dest == 'tmp':  # TODO remove me
            raise RuntimeError('EmcUrl: You must use "::tmp::" now !!!')
        elif dest:
            # create dest path if necessary,
            dirname = os.path.dirname(dest)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            # remove destination file if exists (overwrite)
            if os.path.exists(dest):
                os.remove(dest)
        else:
            raise RuntimeError('EmcUrl: invalid dest')

        self._url = url
        self._dest = dest
        self._min_size = min_size
        self._done_cb = done_cb
        self._prog_cb = prog_cb
        self._cb_args = args
        self._cb_kargs = kargs
        self._headers = headers
        self._decode = decode

    def __repr__(self):
        return '<EmcUrl dest:"{0._dest}">'.format(self)

    @abstractmethod
    def delete(self) -> None:
        """ Abort the corrent download and delete the class """
        del self  # not sure about this :/

    @property
    def url(self) -> str:
        return self._url

    @property
    def dest(self) -> str:
        return self._dest

    def _notify_done(self, success: bool, data: bytes=None):
        """ utility for backends
        Params:
            status (bool): True is success
            data (bytes): received data (in case of ::mem:: download)
        """

        # if file size or data size < min_size: report as error
        if success and self._min_size:
            if self._dest == '::mem::':
                if len(data) < self.min_size:
                    success = False
            else:
                if os.path.getsize(self.dest) < self.min_size:
                    success = False

        # on errors delete the downloaded file
        if not success and self.dest != '::mem::' and os.path.exists(self.dest):
            os.remove(self.dest)

        # call the user callback
        if callable(self._done_cb):
            if self.dest == '::mem::':
                if self._decode == 'utf8':
                    data = data.decode('utf8')
                elif not self._decode:
                    pass  # no decoding at all
                elif self._decode == 'json':
                    raise NotImplementedError('EmcUrl: Json decoder to be done')
                else:
                    raise RuntimeError('EmcUrl: Unknown decode method "{}"'
                                       .format(self._decode))
            else:
                data = self.dest  # data is the destination file path
            self._done_cb(self, success, data,
                          *self._cb_args, **self._cb_kargs)

    def _notify_prog(self, total: int, received: int):
        """ utility for backends
        Params:
            total: total download size in bytes
            current: current downloaded bytes
        """
        if callable(self._prog_cb):
            self._prog_cb(self, total, received,
                          *self._cb_args, **self._cb_kargs)

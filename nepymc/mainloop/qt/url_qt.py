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

from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, \
    QNetworkReply

from nepymc.mainloop import EmcUrl


# a single (lazy loaded) global QNetworkAccessManager instance
_manager = None


class EmcUrl_Qt(EmcUrl):
    """ PySide2 implementation of the EmcUrl abstract"""

    def __init__(self, *args, **kargs):

        super().__init__(*args, **kargs)

        # lazy creation of the NetworkManager
        global _manager
        if _manager is None:
            _manager = QNetworkAccessManager()

        # open the destination file for writing
        if self.dest and self.dest != '::mem::':
            try:
                self._dest_fp = open(self.dest, 'wb')
            except OSError:
                self._notify_done(False)
                return
        else:
            self._dest_fp = None

        # build and send the GET request
        request = QNetworkRequest(self.url)
        if self._headers is not None:
            for key in self._headers:
                request.setHeader(key, self._headers[key])
        self._reply = _manager.get(request)
        self._reply.finished.connect(self._finished_cb)
        self._reply.downloadProgress.connect(self._progress_cb)
        if self.dest != '::mem::':
            self._reply.readyRead.connect(self._data_ready_cb)

    def delete(self) -> None:
        if super().delete() is True:
            self._reply.abort()
            del self._reply

        if self._dest_fp:
            self._dest_fp.close()
            self._dest_fp = None

    def _progress_cb(self, received, totals):
        self._notify_prog(totals, received)

    def _finished_cb(self):
        if self._dest_fp:
            self._dest_fp.close()
            self._dest_fp = None

        if self._reply.error() == QNetworkReply.NoError:
            if self.dest == '::mem::':
                qbytearray = self._reply.readAll()
                self._notify_done(True, qbytearray.data())
            else:
                self._notify_done(True)
        else:
            self._notify_done(False)

    def _data_ready_cb(self):
        # write received data to file
        if self._dest_fp:
            self._dest_fp.write(self._reply.readAll().data())

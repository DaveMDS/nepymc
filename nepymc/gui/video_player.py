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


class EmcVideoPlayer(EmcBackendableABC):
    """ TODO DOC """
    backendable_pkg = 'gui'
    backendable_cls = 'EmcVideoPlayer'

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def delete(self) -> None:
        """ TODOC """

    @property
    @abstractmethod
    def url(self) -> str:
        """ TODOC """

    @url.setter
    @abstractmethod
    def url(self, url: str):
        """ TODOC """

    @property
    @abstractmethod
    def position(self) -> int:
        """ millis """

    @position.setter
    @abstractmethod
    def position(self, val: int):
        """ millis """

    @property
    @abstractmethod
    def duration(self) -> int:
        """ millis """

    @abstractmethod
    def volume_set(self, val: float) -> None:
        """ 0 - 100  (logaritmic adjusted) """

    @abstractmethod
    def play(self) -> None:
        """ start playback """

    @abstractmethod
    def pause(self) -> None:
        """ pause playback """

    @abstractmethod
    def stop(self) -> None:
        """ stop playback """

    @abstractmethod
    def title_set(self, title: str) -> None:
        """ TODOC """

    @abstractmethod
    def poster_set(self, poster: str) -> None:
        """ TODOC """


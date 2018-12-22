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

from abc import ABC, abstractmethod

from nepymc.model import EmcModelViewInterface
from nepymc.mainloop_base import EmcMainLoop_Base


def LOG(*args):
    print('GUI_BASE:', *args)


def DBG(*args):
    print('GUI_BASE:', *args)
    pass


class EmcGui_Base(ABC):
    def __init__(self, mainloop: EmcMainLoop_Base, theme_name: str):
        DBG('Window.__init__()')
        self._mainloop = mainloop
        self._theme_name = theme_name

    @abstractmethod
    def create(self) -> bool:
        return False

    @abstractmethod
    def destroy(self) -> None:
        pass

    @abstractmethod
    def activate_section(self, section: str) -> None:
        """ sections: mainmenu,browser """

    @abstractmethod
    def hide_section(self, section: str) -> None:
        """ sections: mainmenu,browser """

    @abstractmethod
    def model_set(self, section: str, model: EmcModelViewInterface):
        """
        :param section:
        :param model:
        :return:
        """

    @abstractmethod
    def page_title_set(self, title: str):
        """ Set the main title """

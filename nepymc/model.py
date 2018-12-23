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


class EmcModelViewInterface(ABC):
    """ Generic model class """

    #
    # ----  Abstracts for the model implementation (called by the view)
    #
    @abstractmethod
    def item_data_get(self, index, field_name):
        """ The view request data to the model """

    @abstractmethod
    def item_count_get(self):
        """ The view request the items count to the model """

    @abstractmethod
    def item_selected(self, index):
        """ The view notify the model that an item has been selected """

    #
    # ----  Hooks for views (called by the model implementation)
    #
    def view_reset(self):
        """ The model has changed and request the view to reset """
        raise NotImplementedError('The view are not hooking into reset()')

    def select_item(self, index):
        """ The model request the view to show the given index """

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


class EmcModel(object):
    """ Generic model class """
    def __init__(self):
        pass

    def data_get(self, index, field_name):
        pass

    def count_get(self):
        pass

    """
    def roleNames(self):
        return {
            self.label_role: b'label',
            self.icon_role: b'icon',
            self.subitems_role: b'subItems',
        }

    def rowCount(self, index):
        return len(self.items)

    def data(self, index, role):
        # print("***** data(%s, %s)" % (index.row(), role))
        item = self.items[index.row()]
        if role == self.label_role:
            return item['label']
        elif role == self.icon_role:
            return item['icon']
        elif role == self.subitems_role:
            return item['subitems']
    """

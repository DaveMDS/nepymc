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

import sys
from typing import Callable, Iterable

from nepymc import gui
# from nepymc import input_events
from nepymc.model import EmcModelViewInterface


def LOG(*args):
    print('MAINMENU:', *args)


def DBG(*args):
    print('MAINMENU:', *args)
    pass


def ERR(*args):
    print('MAINMENU ERROR:', *args, file=sys.stderr)


class MenuItem(object):
    def __init__(self, name, weight, label, icon, callback, subitems=None):
        self.name = name
        self.weight = weight
        self.label = label
        self.icon = icon
        self.callback = callback
        self.subitems = subitems or []

    def __repr__(self):
        return '<MenuItem name:{0.name} w:{0.weight}>'.format(self)

    def activate(self, subitem=''):
        if subitem:
            self.callback(subitem)
        else:
            self.callback()


class MainMenuModel(EmcModelViewInterface):
    def __init__(self):
        super().__init__()

    def item_count_get(self):
        return len(_ITEMS)

    def item_data_get(self, index, field_name):
        item = _ITEMS[index]
        return getattr(item, field_name, None)

    def item_selected(self, index):
        item = _ITEMS[index]
        item.activate()  # TODO subitems ??


_ITEMS = []
model = MainMenuModel()

"""
_ITEMS = [
    MenuItem('uitests', 1, 'UI tests', 'icon/star', None, None),
    MenuItem('optical', 2, 'Optical Discs', 'icon/optical', None, [
        {'label': 'Play'},
        {'label': 'Eject'}]),
    MenuItem('music', 3, 'Musica', 'icon/music', None, [
        {'label': 'Artists'},
        {'label': 'Albums'},
        {'label': 'Songs'}]),
    MenuItem('film', 4, 'Film', 'icon/movie', None, [
        {'label': 'Folder 1'},
        {'label': 'Folder 2'}]),
    MenuItem('tv', 5, 'Serie TV', 'icon/tv', None, None),
    MenuItem('olchannel', 6, 'Canali Online', 'icon/olvideo', None, None),
    MenuItem('photo', 6, 'Photo', 'icon/photo', None, None),
    MenuItem('config', 6, 'Settings', 'icon/config', None, None),
    MenuItem('exit', 6, 'Quit', 'icon/exit', None, None),
]
"""


def init():
    DBG("init")
    item_add('exit', 200, _('Exit'), 'icon/exit',
             # lambda: gui.ask_to_exit()
             lambda: print("pippo")
             )


def item_add(name: str, weight: int, label: str, icon: str,
             callback: Callable[[str], None],
             subitems: Iterable[Iterable[str]] = None):  # TODO wrong typing?
    """
    Params:
        name: unique name for the item
        weight: preferred position
        label: text to show in the gui
        icon: name of the icon
        callback: callable to call when the item is selected
        subitems: iterable(label, icon, url)
    """

    item = MenuItem(name, weight, label, icon, callback, subitems)
    DBG('ADD', item)

    for pos, before in enumerate(_ITEMS):
        if weight < before.weight:
            break
    else:
        pos = len(_ITEMS)

    DBG('ADD {} W: {} at pos: {}'.format(name, weight, pos))
    _ITEMS.insert(pos, item)


def item_del(name: str) -> None:
    for item in _ITEMS:
        if item.name == name:
            _ITEMS.remove(item)
            break


def item_activate(name: str) -> None:
    for item in _ITEMS:
        if item.name == name:
            break
    else:
        print('WARNING: cannot find the requested activity: "%s"' % name)
        return

    subitem = None  # TODO item.data['sublist'].selected_item
    item.activate(subitem)


def show():
    gui.activate_section('mainmenu')
    # input_events.listener_add('mainmenu', input_event_cb)


def hide():
    # input_events.listener_del('mainmenu')
    gui.hide_section('mainmenu')


# ****************************************************************************
# ****************************************************************************
# ****************************************************************************

"""
def item_add_OLD(name, weight, label, icon, callback, subitems=[]):
    # print('ADD ' + name + ' W ' + str(weight) + ' before ' + str(before.text if before else None))

    img = gui.load_image(icon)

    sublist = gui.EmcList(_list, style='mainmenu_sublist',
                          name='MainMenuSubList',
                          focus_allow=False, focus_on_select=False)
    for _label, _icon, _url in subitems:
        si = sublist.item_append(_label,
                                 gui.load_icon(_icon) if _icon else None)
        si.data['url'] = _url

    before = None
    for it in _list.items:
        if weight <= it.data['weight']:
            before = it
            break

    if before:
        item = _list.item_insert_before(before, label, img, sublist)
    else:
        item = _list.item_append(label, img, sublist)

    item.data['sublist'] = sublist
    item.data['weight'] = weight
    item.data['name'] = name
    item.data['callback'] = callback


def _cb_item_selected(li, item):
    item.bring_in()
    sublist = item.data['sublist']
    if sublist and sublist.selected_item:
        sublist.selected_item.selected = False


def _cb_item_activated(li, item):
    callback = item.data['callback']
    subitem = item.data['sublist'].selected_item
    if subitem:
        callback(subitem.data['url'])
    else:
        callback()

"""


"""
def input_event_cb(event):
    if not _list.focus:
        return input_events.EVENT_CONTINUE

    item = _list.selected_item
    if not item:
        item = _list.first_item
        item.selected = True

    elif event == 'DOWN':
        sublist = item.data['sublist']
        subitem = sublist.selected_item
        if subitem and subitem.next:
            subitem.next.selected = True
        elif not subitem and sublist.first_item:
            sublist.first_item.selected = True
        else:
            return input_events.EVENT_CONTINUE
        return input_events.EVENT_BLOCK

    elif event == 'UP':
        sublist = item.data['sublist']
        subitem = sublist.selected_item
        if subitem and subitem.prev:
            subitem.prev.selected = True
        elif subitem:
            subitem.selected = False
        else:
            return input_events.EVENT_CONTINUE
        return input_events.EVENT_BLOCK

    elif event == 'OK':
        _cb_item_activated(_list, item)
        return input_events.EVENT_BLOCK

    elif event == 'EXIT':
        gui.ask_to_exit()
        return input_events.EVENT_BLOCK

    return input_events.EVENT_CONTINUE
"""
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

from nepymc.modules import EmcModule
from nepymc.browser import EmcItemClass
from nepymc.gui import EmcDialog
from nepymc import input_events
from nepymc import config_gui
from nepymc import gui
from nepymc import ini


def DBG(*args):
    # print('KEYB:', *args)
    pass


class KeyboardModule(EmcModule):
    name = 'input_keyb'
    label = _('Input - Keyboard')
    icon = 'icon/keyboard'
    info = _('The keyboard module lets you control the application using '
             'your keyboard, or any other device that act as a keyboard.')

    def __init__(self):
        DBG('Init module')

        self.grab_key_func = None

        # set up default bindings
        section = 'keyboard'
        if not ini.has_section(section):
            ini.add_section(section)
            defs = gui.instance().default_keymap_get()
            for key, event in defs.items():
                ini.set(section, key, event)

        # read mapping from config
        self.keys = dict()
        for key, event in ini.get_options(section):
            DBG('Map key "%s" to event %s' % (key, event))
            self.keys[key] = event

        # add an entry in the config gui section
        config_gui.root_item_add('keyb', 50, _('Keyboard'),
                                 icon='icon/keyboard',
                                 callback=self.config_panel_cb)

        # ask the gui to forward key events to us
        gui.instance().key_down_connect(self._key_down_cb)

    def __shutdown__(self):
        DBG('Shutdown module')
        config_gui.root_item_del('keyb')
        gui.instance().key_down_connect(None)

    def _key_down_cb(self, key):
        DBG('Key: %s' % key)
        key = key.lower()

        # if grabbed request call the grab function, else emit the signal
        if self.grab_key_func and callable(self.grab_key_func):
            self.grab_key_func(key)
        else:
            try:
                input_events.event_emit(self.keys[key])
            except KeyError:
                print('Not mapped key: ' + key)

    # ---- config panel stuff ----
    class KeyItemClass(EmcItemClass):
        def item_selected(self, url, data):
            key, event, mod = data
            txt = '%s<br><br>%s ⇾ %s' % (
                  _('Are you sure you want to remove the mapping?'),
                  key, event)
            EmcDialog(style='yesno', title=_('Remove key'), text=txt,
                      done_cb=self._remove_confirmed, user_data=data)

        def _remove_confirmed(self, dia):
            key, event, mod = dia.data_get()

            # remove key from mapping and from config
            mod.keys.pop(key, None)
            ini.remove_option('keyboard', key)

            # kill the dialog and refresh the browser
            bro = config_gui.browser_get()
            bro.refresh(hard=True)
            dia.delete()

        def label_get(self, url, data):
            key, event, mod = data
            return key

        def label_end_get(self, url, data):
            key, event, mod = data
            return event

        def icon_get(self, url, data):
            return 'icon/key'

    def config_panel_cb(self):
        bro = config_gui.browser_get()
        bro.page_add('config://keyb/', _('Keyboard'), None, self.populate_keyb)

    def populate_keyb(self, browser, url):
        config_gui.standard_item_action_add(_('Add a new key'),
                                            icon='icon/plus',
                                            cb=self._add_item_cb)
        for key, event in sorted(self.keys.items(), key=lambda x: x[1]):
            browser.item_add(self.KeyItemClass(), 'config://keyb/button',
                             (key, event, self))

    def _add_item_cb(self):
        # grab the next pressed key and show the first dialog
        self.grab_key_func = self.grabbed_key_func
        self.dia = EmcDialog(title=_('Add a new key'), style='cancel',
                             text=_('Press a key on your keyboard'),
                             canc_cb=self.ungrab_key)

    def ungrab_key(self, dialog):
        self.grab_key_func = None
        dialog.delete()

    def grabbed_key_func(self, key):
        # ungrab remote keys & delete the first dialog
        self.grab_key_func = None
        self.pressed_key = key
        self.dia.delete()

        # create the dialog to choose the event to bind
        dia = EmcDialog(title=_('Choose an event to bind'), style='list',
                        done_cb=self.event_choosed_cb)
        for event in input_events.STANDARD_EVENTS.split():
            dia.list_item_append(event)
        dia.list_go()

    def event_choosed_cb(self, dia):
        event = str(dia.list_item_selected_get().label)
        key = str(self.pressed_key)

        # save the pressed key in mapping and config
        self.keys[key] = event
        ini.set('keyboard', key, event)

        # kill the dialog and refresh the browser
        dia.delete()
        bro = config_gui.browser_get()
        bro.refresh(hard=True)

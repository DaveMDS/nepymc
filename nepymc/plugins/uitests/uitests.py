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
import sys

from nepymc.modules import EmcModule
from nepymc import mainmenu
from nepymc import mediaplayer
from nepymc import storage
from nepymc import utils
from nepymc import gui
from nepymc.themoviedb import CastPanel
from nepymc.mainloop import EmcTimer, EmcIdler, EmcUrl, EmcExe
from nepymc.browser import EmcBrowser, \
    EmcItemClass, BackItemClass, FolderItemClass
from nepymc.gui import EmcDialog, EmcNotify, \
    EmcSourcesManager, EmcFolderSelector
# from epymc.gui import  EmcVKeyboard, EmcFolderSelector, \
#    EmcButton, EmcMenu, DownloadManager, EmcSlider

# import epymc.events as events
# import epymc.ini as ini
# from epymc.musicbrainz import MusicBrainz


def DBG(*args):
    print('UITESTS:', *args)
    pass


LOREM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum
consectetur est laoreet est consequat ultricies. Vivamus lectus tellus, egestas
condimentum sollicitudin dictum, congue ac quam. Proin eu erat arcu. Ut tellus
augue, consectetur at lacinia ac, pharetra ornare leo. Quisque ut metus sit
amet risus luctus condimentum. Suspendisse sodales suscipit arcu ut interdum.
Aenean luctus, leo in lacinia pretium, felis odio euismod sapien, eu varius
ipsum odio sit amet elit.
"""

TEST_STYLE = """
<center>
<title>Title</title><br>
<subtitle>Subtitle</><br>
<hilight>hilight</> <b>bold</> <i>italic</> <link>link</><br>
<name>name</> <info>info</> <success>success</> <warning>warning</> <failure>failure</><br>
<bigger>bigger</> <big>big</> normal <small>small</> <smaller>smaller</>
</center>
"""

_mod = None  # global module class instance
_browser = None  # global browser instance

"""
class EncodingItemClass(EmcItemClass):
   TMDB_API_KEY = '19eef197b81231dff0fd1a14a8d5f863'

   def label_get(self, url, user_data):
      return(user_data)

   def info_get(self, url, user_data):
      from epymc.extapi.onlinevideo import fetch_url, call_ydl, url_encode
      
      if url == 'test1': # tmdb.org json parser
         try:
            url = 'http://api.themoviedb.org/3/movie/129?api_key={}&language=it'.format(self.TMDB_API_KEY)
            data = fetch_url(url, parser='json')
            info = 'Test 1 OK<br>Title: {}<br>Original: {}'.format(data['title'], data['original_title'])
            return info
         except Exception as e:
            return repr(e)

      if url == 'test2': # tmdb.org url encode
         try:
            url = 'http://api.themoviedb.org/3/search/movie/?{}'.format(
                   url_encode({'query':'la città incantata',
                               'api_key':self.TMDB_API_KEY,
                               'language': 'it'}))
            data = fetch_url(url, parser='json')['results'][0]
            info = 'Test 2 OK<br>Title: {}<br>Original: {}'.format(data['title'], data['original_title'])
            return info
         except Exception as e:
            return repr(e)

      if url == 'test3': # tmdb.org virtual keyboard
         def _done_cb(keyb, text):
            try:
               url = 'http://api.themoviedb.org/3/search/movie/?{}'.format(
                      url_encode({'query':text,
                                  'api_key':self.TMDB_API_KEY,
                                  'language': 'it'}))
               data = fetch_url(url, parser='json')['results'][0]
               info = 'Test 3 OK<br>Title: {}<br>Original: {}'.format(data['title'], data['original_title'])
               EmcDialog(title='test3 result', text=info)
            except Exception as e:
               EmcDialog(title='test3 result', text=repr(e))

         EmcVKeyboard(title='Just press Accept!', text='千と千尋の神隠し',
                      accept_cb=_done_cb)
"""

""" 
class MyItemClass(EmcItemClass):

   def label_get(self, url, user_data):
      if url == 'uitest://styles':
         return 'Text styles <small>(<b>bold</b> <i>italic</i> <info>info</info> ' \
                '<success>success</success> <failure>failure</failure> <warning>warning</warning>)</small>'
      else:
         return user_data

   def info_get(self, url, user_data):
      if url == 'uitest://styles':
         return TEST_STYLE

   def item_selected(self, url, user_data):

      # Sub-pages
      if url == 'uitest://encoding':
         _mod._browser.page_add('uitest://encoding', 'Encoding tests', None,
                                _mod.populate_encoding_page)

      elif url == 'uitest://views':
         _mod._browser.page_add('uitest://views', 'Browser Views',
                                ('List', 'PosterGrid', 'CoverGrid'),
                                _mod.populate_views_page)

      # Events Sniffer
      elif url == 'uitest://sniffer':
         events.listener_add('sniffer', lambda ev: EmcNotify('<title>Event sniffer</><br>' + ev))
         n = EmcNotify('Sniffer enabled.', hidein = 2)

      # Event Emit
      elif url == 'uitest://ev_emit':
         events.event_emit('TEST_EVENT')

      # Menu
      elif url == 'uitest://menu':
         def _cb_menu(menu, item):
            print("Selected item: " + item.text)

         m = EmcMenu()
         m.item_add("Item 1", callback=_cb_menu)
         m.item_add("Item 2", callback=_cb_menu)
         m.item_add("Item 3", callback=_cb_menu)
         m.item_separator_add()
         m.item_add("Item 4", "icon/evas", callback=_cb_menu)
         m.item_add("Item 5", "icon/home", "icon/volume", callback=_cb_menu)
         m.item_separator_add()
         it = m.item_add("Disabled", callback=_cb_menu)
         it.disabled = True
         it = m.item_add("Disabled", 'icon/home', callback=_cb_menu)
         it.disabled = True
         m.item_add("Item 8", None, 'icon/volume', callback=_cb_menu)
         it = m.item_add("Item 9 (disabled)", callback=_cb_menu)
         it.disabled = True
         m.show()

      elif url == 'uitest://menu_long':
         def _cb_menu(menu, item):
            print('Selected item: ' + item.text)

         m = EmcMenu(dismiss_on_select=False)
         for i in range(1, 100):
            m.item_add('Item %d' % i, 'icon/home', 'icon/volume', callback=_cb_menu)
         m.show()

      # TMDB
      # elif url == 'uitest://tmdb':
         # s = TMDB_WithGui()
         # s.movie_search('alien')

      # Download Manager
      elif url == 'uitest://dm':
         DownloadManager().queue_download('http://fredrik.hubbe.net/plugger/xvidtest.avi', 'dm_test1')
         DownloadManager().queue_download('http://www.archive.org/download/TheMakingOfSuzanneVegasSecondLifeGuitar/3-TheMakingOfSuzanneVega_sSecondLifeGuitar.mp4', 'TheMakingOfSuzanneVega')

      elif url == 'uitest://dm2':
         DownloadManager().in_progress_show()
         
      # VKeyboard
      elif url == 'uitest://vkbd':
         EmcVKeyboard(title='Virtual Keyboard', text='This is the keyboard test!',
                      accept_cb=lambda vk, t: print('ACCEPT "%s"' % t),
                      dismiss_cb=lambda vk: print('DISMISS'))

      # Browser Dump
      elif url == 'uitest://brdump':
         DBG('Dumping Browser')
         browser.dump_everythings()

      # Buttons Theme + Focus
      elif url == 'uitest://buttons':
         def _buttons_cb(btn):
            print(btn)

         vbox0 = Box(gui.win)
         vbox0.show()

         hbox = Box(gui.win)
         hbox.horizontal_set(True)
         hbox.show()
         vbox0.pack_end(hbox)

         d = EmcDialog(title='button test', content=vbox0, style='panel')

         ### Active buttons
         vbox = Box(gui.win)
         vbox.show()
         # label
         b = EmcButton(d, 'only label', cb=_buttons_cb)
         vbox.pack_end(b)
         # icon
         b = EmcButton(d, icon='icon/star', cb=_buttons_cb)
         b.focus = True
         vbox.pack_end(b)
         # label + icon
         b = EmcButton(d, 'label + icon', 'icon/star', cb=_buttons_cb)
         vbox.pack_end(b)
         hbox.pack_end(vbox)

         ### Disabled buttons
         vbox = Box(gui.win)
         vbox.show()
         # label
         b = EmcButton(d, 'only label disabled', cb=_buttons_cb)
         b.disabled_set(True)
         vbox.pack_end(b)
         # icon
         b = EmcButton(d, icon='icon/mame', cb=_buttons_cb)
         b.disabled_set(True)
         vbox.pack_end(b)
         # label + icon
         b = EmcButton(d, 'label + icon disabled', 'icon/back', cb=_buttons_cb)
         b.disabled_set(True)
         vbox.pack_end(b)
         hbox.pack_end(vbox)

         # toggle buttons
         hbox2 = Box(gui.win)
         hbox2.horizontal_set(True)
         hbox2.show()
         b = EmcButton(d, 'toggle label', toggle=True, cb=_buttons_cb)
         hbox2.pack_end(b)
         b = EmcButton(d, 'toggle label + icon', 'icon/star', toggle=True, cb=_buttons_cb)
         hbox2.pack_end(b)
         b = EmcButton(d, icon='icon/star', toggle=True, cb=_buttons_cb)
         hbox2.pack_end(b)
         b = EmcButton(d, icon='icon/star', toggle=True, cb=_buttons_cb)
         b.toggled = True
         hbox2.pack_end(b)
         b = EmcButton(d, 'toggle disabled', 'icon/star', toggle=True, cb=_buttons_cb)
         b.disabled_set(True)
         hbox2.pack_end(b)
         vbox0.pack_end(hbox2)

         # 7 butttons in a row (numbers)
         hbox2 = Box(gui.win)
         hbox2.horizontal_set(True)
         hbox2.show()
         for i in range(0,8):
            b = EmcButton(d, str(i), cb=_buttons_cb)
            hbox2.pack_end(b)
         vbox0.pack_end(hbox2)

         # mediaplayer buttons
         hbox2 = Box(gui.win)
         hbox2.horizontal_set(True)
         hbox2.show()
         icons = ['icon/prev', 'icon/fbwd','icon/bwd','icon/stop','icon/play','icon/fwd','icon/ffwd','icon/next']
         for i in icons:
            b = EmcButton(d, icon=i, cb=_buttons_cb)
            hbox2.pack_end(b)
         vbox0.pack_end(hbox2)

         # all the icons of the theme in buttons
         i = 0
         for group in edje.file_collection_list(gui.theme_file):
            if group.startswith('icon/'):
               if i % 16 == 0:
                  hbox2 = Box(gui.win, horizontal=True)
                  vbox0.pack_end(hbox2)
                  hbox2.show()
               b = EmcButton(d, icon=group, cb=_buttons_cb)
               hbox2.pack_end(b)
               i += 1

      elif url.startswith('uitest://focus_'):
         grid = Grid(gui.win, size=(100, 100))
         d = EmcDialog(title='Focus corner cases', content=grid, style='panel')

         def btn_add(label, x, y, w, h, focus=False):
            bt = EmcButton(d, label)
            grid.pack(bt, x, y, w, h)
            bt.focus = focus

         if url.endswith('1'):
            btn_add('top',    40,  0, 20, 10, True)
            btn_add('bottom', 40, 90, 20, 10)
            btn_add('left',    0, 45, 20, 10)
            btn_add('right',  80, 45, 20, 10)

         elif url.endswith('2'):
            btn_add('top L',   0,  0, 20, 10)
            btn_add('top R',  80,  0, 20, 10)
            btn_add('bot L',   0, 90, 20, 10)
            btn_add('bot R',  80, 90, 20, 10)
            btn_add('center', 40, 40, 20, 10, True)

         elif url.endswith('3'):
             btn_add('top',    40,  0, 20, 10)
             btn_add('bottom', 40, 90, 20, 10)
             btn_add('left',    0, 45, 20, 10)
             btn_add('right',  80, 45, 20, 10)
             btn_add('top L',   0,  0, 20, 10)
             btn_add('top R',  80,  0, 20, 10)
             btn_add('bot L',   0, 90, 20, 10)
             btn_add('bot R',  80, 90, 20, 10)
             btn_add('center', 40, 45, 20, 10, True)

      # Sliders
      elif url == 'uitest://sliders':
         vbox = Box(gui.win)
         d = EmcDialog(title='Slider test', content=vbox, style='panel')

         # normal
         sl = EmcSlider(d, value=0.5, indicator_show=False,
                        size_hint_fill=FILL_HORIZ)
         vbox.pack_end(sl)
         sl.focus = True

         # icons
         sl = EmcSlider(d, value=0.5,  indicator_show=False,
                        size_hint_fill=FILL_HORIZ)
         sl.part_content_set('icon', gui.load_icon('icon/evas'))
         sl.part_content_set('end', gui.load_icon('icon/check_on'))
         vbox.pack_end(sl)

         # with text
         sl = EmcSlider(d, text='with text', value=0.5, indicator_show=False,
                        size_hint_fill=FILL_HORIZ)
         vbox.pack_end(sl)

         # no focus
         sl = EmcSlider(d, text='no focus', value=0.5, indicator_show=False,
                        focus_allow=False, size_hint_fill=FILL_HORIZ)
         vbox.pack_end(sl)

         # unit + indicator format
         sl = EmcSlider(d, text='indicator', min_max=(-1.0, 3.0),
                        unit_format='%.2f u', indicator_format='%.1f u',
                        indicator_show_on_focus=True,
                        size_hint_fill=FILL_HORIZ)
         vbox.pack_end(sl)

         # disabled
         sl = EmcSlider(d, text='disabled', unit_format='unit', value=0.5,
                        disabled=True, size_hint_fill=FILL_HORIZ)
         vbox.pack_end(sl)

      # Icons gallery
      elif url == 'uitest://icons':
         d = EmcDialog(title='Icons gallery', style='list')
         for group in sorted(edje.file_collection_list(gui.theme_file)):
            if group.startswith('icon/'):
               d.list_item_append(group[5:], group)
         d.list_go()

      # Images gallery
      elif url == 'uitest://imagegal':
         d = EmcDialog(title='Images gallery (names in console)',
                       style='image_list_horiz',
                       done_cb=lambda x, t: print(t))
         for group in sorted(edje.file_collection_list(gui.theme_file)):
            if group.startswith('image/'):
               d.list_item_append(group[6:], group, t=group)
         d.list_go()

      # Text style in dialog
      elif url == 'uitest://styles':
         EmcDialog(title='Text styles', text=TEST_STYLE)

      # Music Brainz AudioCD 
      elif url == 'uitest://mbrainz':
         def info_cb(album):
            txt = utf8_to_markup(pprint.pformat(album))
            EmcDialog(title='Result', text='<small>{}</>'.format(txt))

         # musicbrainz.calculate_discid('/dev/sr0')
         MusicBrainz().get_cdrom_info('/dev/cdrom', info_cb, ignore_cache=True)
         

      # Movie name test
      # elif url == 'uitest://movies_name':
         # urls = [ 'alien.avi',
                  # 'alien (1978).avi',
                  # '(2003)alien 3.avi',
                  # '[DivX - ITA] alien 3.avi',
                  # '[DivX - ITA] ali]en 3.avi',
                  # '[DivX - ITA] al[i]en 3.avi',
                  # '[DivX - ITA]alien3.avi',
                  # '[DivX - ITA]   alien3   .avi',
                  # '[DivX - ITA]alien.3.la.clonazione.avi',
                  # '[DivX - ITA]alien 3 - la clonazione.avi',
                  # '{DivX - ITA} alien 3.avi',
                  # 'alien {DivX - ITA}.avi',
                  # '[DivX - ITA] Die Hard I - Trappola di Cristallo.avi',
                # ]
         # t = ''
         # for u in urls:
            # t += '<hilight>URL:</> ' + u + '<br>'
            # t += '<hilight>name/year:</> ' + str(get_movie_name_from_url(u)) + '<br><br>'
         # EmcDialog(title = 'Movie name test', text = t)
"""


class GenericItemClass(EmcItemClass):

    def label_get(self, url, user_data):
        return user_data

    def info_get(self, url, user_data):
        return '<title>Test name:</title><br>' + user_data


class Test_Styles(GenericItemClass):
    def label_get(self, url, user_data):
        return \
            'Text styles <small>(<b>bold</b> <i>italic</i> <info>info</info> ' \
            '<success>success</success> <failure>failure</failure> ' \
            '<warning>warning</warning>)</small>'

    def info_get(self, url, user_data):
        return TEST_STYLE


class Test_Buttons(GenericItemClass):
    def item_selected(self, url, user_data):
        print("BUTTON", url, user_data)


class Test_Focus(GenericItemClass):
    def item_selected(self, url, user_data):
        print("FOCUS", url, user_data)


class Test_Timer(GenericItemClass):
    def __init__(self):
        super().__init__()
        self.dialog = None
        self.timer = None
        self.iter_count = 0

    def item_selected(self, url, user_data):
        self.timer = None
        self.dialog = dia = EmcDialog('EmcTimer test', 'Press "create"')
        dia.on_delete(self.dialog_deleted, dkey1='val1', dkey2=2)
        dia.button_add('Close test', lambda b: self.dialog.delete())
        dia.button_add('delete()', lambda b: self.timer.delete())
        dia.button_add('stop()', lambda b: self.timer.stop())
        dia.button_add('start()', lambda b: self.timer.start())
        dia.button_add('reset()', lambda b: self.timer.reset())
        dia.button_add('Create oneshot', self.timer_create_oneshot)
        dia.button_add('Create onstart', self.timer_create_onstart)

    def timer_create_onstart(self, btn):
        self.iter_count = 0
        self.timer = EmcTimer(1.0, self.timer_cb, parent=self.dialog,
                              onstart=True, key1='V1', key2='V2')

    def timer_create_oneshot(self, btn):
        self.iter_count = 0
        self.timer = EmcTimer(1.0, self.timer_cb, parent=self.dialog,
                              oneshot=True, key1='V1', key2='V2')

    def timer_cb(self, key1=None, key2=None):
        assert key1 == 'V1'
        assert key2 == 'V2'
        self.iter_count += 1
        self.dialog.text_set('Triggered: %d<br>key1=%s key2=%s' % (
                             self.iter_count, key1, key2))

    def dialog_deleted(self, dia, dkey1, dkey2):
        assert dia is self.dialog
        assert dkey1 == 'val1'
        assert dkey2 == 2
        assert self.dialog.deleted is True
        assert self.timer is None or self.timer.deleted is True
        del self.dialog  # remove our reference
        del self.timer  # remove our reference


class Test_Idler(GenericItemClass):
    def __init__(self):
        super().__init__()
        self.dialog = None
        self.idler = None
        self.iter_count = 0

    def item_selected(self, url, user_data):
        self.dialog = dia = EmcDialog('EmcIdler test', 'Press "create"')
        dia.button_add('Close test', self.close_test)
        dia.button_add('delete()', lambda b: self.idler.delete())
        dia.button_add('resume()', lambda b: self.idler.resume())
        dia.button_add('pause()', lambda b: self.idler.pause())
        dia.button_add('Create oneshot', self.idler_create_oneshot)
        dia.button_add('Create', self.idler_create)

    def idler_create(self, btn):
        self.iter_count = 0
        self.idler = EmcIdler(self.idler_cb, parent=self.dialog)

    def idler_create_oneshot(self, btn):
        self.iter_count = 0
        self.idler = EmcIdler(self.idler_cb, parent=self.dialog, oneshot=True,
                              key1="V1", key2="V2")

    def idler_cb(self, key1=None, key2=None):
        self.iter_count += 1
        self.dialog.text_set("Triggered: %d<br>key1=%s key2=%s" % (
                             self.iter_count, key1, key2))

    def close_test(self, btn):
        self.dialog.delete()
        self.idler = None
        self.dialog = None


class Test_MediaPlayer(GenericItemClass):
    def item_selected(self, url, user_data):

        # Mediaplayer Local Video
        if url == 'uitest://mpv':
            f = os.path.expanduser('~/Video/testvideo.avi')
            # f = os.path.expanduser('~/Video/testvideo.mp4')
            mediaplayer.play_url(f)  # , start_from=0)
            mediaplayer.title_set('Testing title')
            mediaplayer.poster_set('image/dvd_cover_blank.png')

        # Mediaplayer Online Video (good)
        elif url == 'uitest://mpvo':
            mediaplayer.play_url('http://trailers.apple.com/movies/independent/'
                                 'airracers/airracers-tlr1_h480p.mov')
            # http://samples.mplayerhq.hu/
            # http://download.wavetlan.com/SVV/Media/HTTP/http-mp4.htm

        # Mediaplayer Online Video (bad)
        elif url == 'uitest://mpvob':
            mediaplayer.play_url('http://www.archive.org/download/'
                                 'TheMakingOfSuzanneVegasSecondLifeGuitar/3-'
                                 'TheMakingOfSuzanneVega_sSecondLifeGuitar.mp4')

        # Mediaplayer DVD
        elif url == 'uitest://dvd':
            mediaplayer.play_url('dvd:///dev/cdrom')


class Test_Browser(GenericItemClass):

    path = os.path.dirname(__file__)

    def item_selected(self, url, user_data):
        # main item
        if url == 'uitest://browser':
            _browser.page_add(url, user_data, None, self.populate_subpage)
        # subitems
        elif url.endswith('/hide'):
            _browser.hide()
        elif url.endswith('/refresh'):
            _browser.refresh()
        elif url.endswith('/refresh_hard'):
            _browser.refresh(hard=True)

    def populate_subpage(self, browser, url):
        browser.item_add(BackItemClass(), url + '/back',
                         'special BackItemClass')
        browser.item_add(FolderItemClass(), url + '/folder',
                         'special FolderItemClass')
        browser.item_add(self, url + '/hide',
                         'browser hide()')
        browser.item_add(self, url + '/refresh',
                         'browser refresh()')
        browser.item_add(self, url + '/refresh_hard',
                         'browser refresh(hard)')
        browser.item_add(self, url + '/one_label',
                         'one label')
        browser.item_add(self, url + '/one_icon',
                         'one icon')
        browser.item_add(self, url + '/two_icons',
                         'two icons')
        browser.item_add(self, url + '/two_labels',
                         'two labels (no info)')
        browser.item_add(self, url + '/two_labels_one_icon',
                         'two labels + one icon')
        browser.item_add(self, url + '/two_labels_two_icon',
                         'two labels + two icon')
        browser.item_add(self, url + '/poster_no_info',
                         'with poster only (no info)')
        browser.item_add(self, url + '/poster',
                         'with poster only')
        browser.item_add(self, url + '/cover',
                         'with cover only')
        browser.item_add(self, url + '/poster_cover',
                         'with poster and cover')

    def label_end_get(self, url, user_data):
        if url.endswith(('/two_labels', '/two_labels_one_icon',
                         '/two_labels_two_icon')):
            return 'second'

    def icon_get(self, url, user_data):
        if url.endswith(('/one_icon', '/two_icons', '/two_labels_one_icon',
                         '/two_labels_two_icon')):
            return 'icon/home'
        if url.endswith(('/poster_no_info', '/poster', '/cover',
                         '/poster_cover')):
            return 'icon/views'

    def icon_end_get(self, url, user_data):
        if url == 'uitest://browser':
            return 'icon/forward'
        if url.endswith(('/two_icons', '/two_labels_two_icon')):
            return 'icon/star'

    def info_get(self, url, user_data):
        if url.endswith(('/two_labels', '/poster_no_info')):
            return None
        return super().info_get(url, user_data)

    def poster_get(self, url, user_data):
        if url.endswith(('/poster', '/poster_cover', '/poster_no_info')):
            return os.path.join(self.path, 'poster.jpg')

    def cover_get(self, url, user_data):
        if url.endswith(('/cover', '/poster_cover')):
            return os.path.join(self.path, 'cover.jpg')


class Test_ImageDialog(GenericItemClass):

    path = os.path.dirname(__file__)
    remote_img = 'https://edmullen.net/test/rc.jpg'  # 5MB png image

    def __init__(self):
        super().__init__()
        self.dia = None

    def item_selected(self, url, user_data):
        self.dia = d = EmcDialog(title="Test EmcImage")
        d.button_add('Close', selected_cb=lambda b: self.dia.delete())
        d.button_add('set(error)', selected_cb=self.from_not_exists)
        d.button_add('set(\'\')', selected_cb=self.unset, cb_data="e")
        d.button_add('set(None)', selected_cb=self.unset, cb_data="n")
        d.button_add('URL dest', selected_cb=self.from_url_with_dest)
        d.button_add('URL auto', selected_cb=self.from_url)
        d.button_add('Image', selected_cb=self.from_image)
        d.button_add('Icon', selected_cb=self.from_icon)
        d.button_add('Fullpath', selected_cb=self.from_fullpath, default=True)

    def from_fullpath(self, btn):
        full = os.path.join(self.path, 'poster.jpg')
        self.dia.content_set(full)

    def from_icon(self, btn):
        self.dia.content_set('icon/home')

    def from_image(self, btn):
        self.dia.content_set('image/dvd_cover_blank.png')

    def from_url(self, btn):
        self.dia.content_set(self.remote_img)

    def from_url_with_dest(self, btn):
        self.dia.content_set((self.remote_img, '/tmp/asdasdasd'))

    def unset(self, btn, value):
        self.dia.content_set('' if value == 'e' else None)

    def from_not_exists(self, btn):
        self.dia.content_set('not_existing_image.png')


class Test_ImageBrowser(GenericItemClass):

    path = os.path.dirname(__file__)
    remote_img = 'https://edmullen.net/test/rc.jpg'  # 5MB png image

    def populate_subpage(self, browser, url):
        # Local images
        browser.item_add(self, os.path.join(self.path, 'poster.jpg'),
                         'From a local full path')
        browser.item_add(self, 'icon/star',
                         'From an icon in the theme')
        browser.item_add(self, 'image/dvd_cover_blank.png',
                         'From an image in the theme')

        # Remote with auto cache
        browser.item_add(self, self.remote_img,
                         'From a remote url (with auto cache) 5MB image')

        # Remote with explicit dest TODO TODO TODO TODO TODO TODO TODO TODO TODO
        browser.item_add(self, ('https://image.tmdb.org/t/p/original/3bKHPDte16BeNLo57W2FwO0jRJZ.jpg', '/tmp/asdasdas'),
                         'From a remote url (with explicit dest) **TODO**')

        # Special styles
        browser.item_add(self, 'special/bd/My cool movie without a poster',
                         'Special Blu-ray')
        browser.item_add(self, 'special/cd/My album without a cover',
                         'Special Compact-disk')
        text = 'This is my special/folder/name <br>' \
               '(can also include "/" and other special chars)<br>' \
               'àèìòù<br>నాన్నకు ప్రేమతో<br>もののけ姫<br><br>...and tags:<br>' \
               + TEST_STYLE
        browser.item_add(self, 'special/folder/' + text,
                         'Special Folder')

        # Unset
        browser.item_add(self, None, 'Unset (None)')
        browser.item_add(self, '', 'Unset (\'\')')

        # TODO test for error cases

        # browser.item_add(self, url + '/special_icon',  # TODO
        #                  'Special Icon (in PosterGrid view)')
        # browser.item_add(self, url + '/special_null',  # TODO  ???
        #                  'Special Null (transparent)')

    def item_selected(self, url, user_data):
        # main item
        if url == 'uitest://imgb':
            _browser.page_add(url, user_data, None, self.populate_subpage)

    def icon_end_get(self, url, user_data):
        if url == 'uitest://imgb':
            return 'icon/forward'

    def icon_get(self, url, user_data):
        if isinstance(url, str) and url.endswith('/special_icon'):
            return 'icon/home'

    def info_get(self, url, user_data):
        if url == 'uitest://imgb':
            return 'Test EmcImage in browser'
        elif url and url.startswith('special/'):
            return None
        else:
            return 'Image url:<br>{}'.format(url)

    def poster_get(self, url, user_data):
        return url if url != 'uitest://imgb' else None


class Test_Dialog(GenericItemClass):

    path = os.path.dirname(__file__)
    cover = os.path.join(path, 'cover.jpg')
    poster = os.path.join(path, 'poster.jpg')
    backdrop = os.path.join(path, 'backdrop.jpg')

    def populate_subpage(self, browser, url):
        browser.item_add(self, url + '/info', 'Dialog - Info')
        browser.item_add(self, url + '/warning', 'Dialog - Warning')
        browser.item_add(self, url + '/warning2', 'Dialog - Warning (no title)')
        browser.item_add(self, url + '/error', 'Dialog - Error')
        browser.item_add(self, url + '/yesno1', 'Dialog - YesNo (callbacks)')
        browser.item_add(self, url + '/yesno2', 'Dialog - YesNo (no callbacks)')
        browser.item_add(self, url + '/cancel', 'Dialog - Cancel')
        browser.item_add(self, url + '/progress', 'Dialog - Progress')
        browser.item_add(self, url + '/progress-btn', 'Dialog - Progress + btns')
        browser.item_add(self, url + '/list', 'Dialog - List')
        browser.item_add(self, url + '/list-btn', 'Dialog - List with buttons')
        browser.item_add(self, url + '/list-img-landscape',
                                     'Dialog - List with images (landscape)')
        browser.item_add(self, url + '/list-img-portrait',
                                     'Dialog - List with images (portrait)')
        browser.item_add(self, url + '/panel1', 'Dialog - Panel full')
        browser.item_add(self, url + '/panel4', 'Dialog - Panel full more')
        browser.item_add(self, url + '/panel2', 'Dialog - Panel no buttons ')
        browser.item_add(self, url + '/panel3', 'Dialog - Panel no title')
        browser.item_add(self, url + '/buffering', 'Dialog - Buffering  **TODO**')

    def icon_end_get(self, url, user_data):
        if url == 'uitest://dialog':
            return 'icon/forward'

    def item_selected(self, url, user_data):
        # main item selected, create the subpage
        if url == 'uitest://dialog':
            _browser.page_add(url, user_data, None, self.populate_subpage)

        # Dialog - Info
        elif url.endswith('/info'):
            print("DIALOG INFO", url, user_data)
            EmcDialog(title='Dialog - Info', text=LOREM, style='info')

        # Dialog - Warning
        elif url.endswith('/warning'):
            text = 'This is an <br><br><b>Warning</><br>dialog<br>'
            EmcDialog(title='Dialog - Warning',
                      text=text, style='warning')

        # Dialog - Warning (no title)
        elif url.endswith('/warning2'):
            text = 'This is an <br><br><b>Warning</><br>dialog<br>'
            EmcDialog(text=text, style='warning')

        # Dialog - Error
        elif url.endswith('/error'):
            text = 'This is an <br><br><b>Error</><br>dialog<br>'
            EmcDialog(title='Dialog - Error', text=text, style='error')

        # Dialog - YesNo (with callbacks)
        elif url.endswith('/yesno1'):
            text = 'This is an <br><br><b>Yes/No</><br>dialog<br>'
            EmcDialog(title='Dialog - YesNo', text=text, style='yesno',
                      done_cb=lambda dia: print('done', dia),
                      canc_cb=lambda dia: print('canc', dia))

        # Dialog - YesNo (without callbacks)
        elif url.endswith('/yesno2'):
            text = 'This is an <br><br><b>Yes/No</><br>dialog<br>'
            EmcDialog(title='Dialog - YesNo', text=text, style='yesno')

        # Dialog - Cancel
        elif url.endswith('/cancel'):
            text = 'This is an <br><br><b>Cancel operation</><br>dialog<br>'
            EmcDialog(title='Dialog - Cancel', text=text,
                      style='cancel', spinner=True)

        # Dialog - Progress
        elif url.startswith('uitest://dialog/progress'):
            def _canc_cb(dialog):
                t.delete()
                d.delete()

            def _progress_timer():
                d.progress_set(self._progress)
                self._progress += 0.01
                if self._progress > 1:
                    self._progress = 0

            text = 'This is a <br><br><b>Progress operation</><br>dialog<br>'
            d = EmcDialog(title='Dialog - Progress', text=text,
                          style='progress', done_cb=_canc_cb,
                          canc_cb=_canc_cb)
            if url.endswith('btn'):
                d.button_add("btn1", selected_cb=lambda b: print('btn1 callback'))
                d.button_add("btn2", selected_cb=lambda b: print('btn2 callback'))
                d.button_add("btn3", selected_cb=lambda b: print('btn3 callback'))
            self._progress = 0.0
            t = EmcTimer(0.2, _progress_timer)

        # Dialog - List
        elif url.endswith('/list'):
            def _dia_list_cb(dia):
                item = dia.list_item_selected_get()
                print('Selected: ' + str(item))
                # dia.delete()
            d = EmcDialog(title='Dialog - List', style='list',
                          done_cb=_dia_list_cb)
            d.list_item_append('item 1', 'icon/home')
            d.list_item_append('item 2', 'icon/star', 'icon/check_on')
            d.list_item_append('item 3 <b>bold</> <info>info</> '
                               '<success>success</> <failure>failure</> '
                               '<i>etc...</>',
                               'icon/star', 'icon/check_on')
            d.list_item_append('item 4', 'icon/tag', 'text/End Text')
            d.list_item_append('item 5', 'icon/tag', 'text/Styled <b>End</> <info>Text</>')
            d.list_item_append('item 6 ' + ('A really long text, ' * 6))
            for i in range(7, 101):
                d.list_item_append('item #%d' % i)
            d.list_go()

        # Dialog - List with buttons
        elif url.endswith('/list-btn'):
            d = EmcDialog(title='Dialog - List with buttons',
                          style='list')
            for i in range(1, 40):
                d.list_item_append('item %d'%i)

            def _btn_cb(b):
                item = d.list_item_selected_get()
                print('Selected:', item)
                d.delete()

            d.button_add('One', selected_cb=_btn_cb)
            d.button_add('Two', selected_cb=_btn_cb)
            d.button_add('Tree', selected_cb=_btn_cb)
            d.list_go()

        # Dialog - Image list (landscape)
        elif url.endswith('/list-img-landscape'):
            d = EmcDialog(title=user_data, style='image_list_landscape',
                          done_cb=lambda x, t: print(t))
            for i in range(20):
                d.list_item_append('item #%d' % i, self.backdrop)
            d.list_go()

        # Dialog - Image list (portrait)
        elif url.endswith('/list-img-portrait'):
            d = EmcDialog(title=user_data, style='image_list_portrait',
                          done_cb=lambda x, t: print(t))
            for i in range(20):
                d.list_item_append('item #%d' % i, self.poster)
            d.list_go()

        # Dialog - Panel full
        elif url.endswith('/panel1'):
            d = EmcDialog(title='Dialog - Panel full', text=LOREM * 8,
                          style='panel', spinner=True)
            d.button_add('One', selected_cb=lambda b: print('btn1 callback'))
            d.button_add('Two', selected_cb=lambda b: print('btn2 callback'))
            d.button_add('Tree', selected_cb=lambda b: print('btn3 callback'))

        # Dialog - Panel full more
        elif url.endswith('/panel4'):
            d = EmcDialog(title='Dialog - Panel full more', text=LOREM * 8,
                          style='panel', spinner=False,
                          content='image/dvd_cover_blank.png')
            d.button_add('One', selected_cb=lambda b: print('btn1 callback'))
            d.button_add('Two', selected_cb=lambda b: print('btn2 callback'))
            d.button_add('Tree', selected_cb=lambda b: print('btn3 callback'))

        # Dialog - Panel no buttons
        elif url.endswith('/panel2'):
            text = LOREM
            d = EmcDialog(title='Dialog - Panel full', text=text,
                          style='panel', spinner=True)

        # Dialog - Panel no title
        elif url.endswith('/panel3'):
            text = LOREM
            d = EmcDialog(text=text, style='panel', spinner=True)

        # Dialog - Buffering ** TODO **
        elif url.endswith('/buffering'):
            def _progress_timer2():
                self._progress += 0.05
                d.progress_set(self._progress)
                if self._progress >= 1.0:
                    d.delete()
                    return False  # stop the timer
                else:
                    return True  # renew the callback

            d = EmcDialog(style='buffering', title=_('Buffering'))
            self._progress = 0.0
            EmcTimer(0.2, _progress_timer2)


class Test_Notify(GenericItemClass):

    def item_selected(self, url, user_data):
        EmcNotify('<title>Title 1</><br>'
                  'With an image. hide in 2 seconds.',
                  image='image/dvd_cover_blank.png',
                  hidein=2)
        n = EmcNotify('Will hide in 10 seconds.', 'icon/check_off', hidein=10)
        n.counter = 11
        EmcTimer(1.0, self._timer_cb, onstart=True, parent=n, notify=n)
        EmcNotify('<title>Title 3</><br>'
                  'This one with an icon',
                  image='icon/movie')
        EmcNotify('<title>Title 4</><br>'
                  'Test longer text and tags.<br>'
                  'Test longer text and tags.<br>'
                  'Test longer text and tags.<br>'
                  '<b>bold</b> <i>italic</i> <u>underline</u> <link>link</link>'
                  ' <info>info</info> <success>success</success>'
                  ' <warning>warning</warning> <failure>failure</failure>.',
                  image='icon/star')

    @staticmethod
    def _timer_cb(notify):
        notify.counter -= 1
        notify.text_set('Will hide in %d seconds' % notify.counter)
        if notify.image == 'icon/check_on':
            notify.image_set('icon/check_off')
        else:
            notify.image_set('icon/check_on')


class Test_BG(GenericItemClass):

    backdrop1 = os.path.join(os.path.dirname(__file__), 'backdrop.jpg')
    backdrop2 = os.path.join(os.path.dirname(__file__), 'backdrop2.jpg')

    def __init__(self):
        super().__init__()
        self.bg = None

    def item_selected(self, url, user_data):
        if self.bg == self.backdrop1:
            self.bg = self.backdrop2
        else:
            self.bg = self.backdrop1
        gui.backdrop_set(self.bg)


class Test_FolderSelector(GenericItemClass):
    def item_selected(self, url, user_data):
        EmcFolderSelector(title='Choose a path or a file',
                          done_cb=self.selector_cb, pippo="pippo", due="due")

    @staticmethod
    def selector_cb(path, pippo, due):
        assert pippo == "pippo"
        assert due == "due"
        print("FolderSelector:", path)


class Test_SourceManager(GenericItemClass):
    def item_selected(self, url, user_data):
        EmcSourcesManager('movies', done_cb=self.manager_cb)

    @staticmethod
    def manager_cb(new_folders_list):
        print("Source Manager:", new_folders_list)


class Test_Storage(GenericItemClass):
    def item_selected(self, url, user_data):

        def storage_events_cb(event):
            if event != 'STORAGE_CHANGED':
                return
            dia.list_clear()
            for device in storage.list_devices():
                txt = '{0.label} [ {0.device} ➙ {0.mount_point} ]'.format(
                    device)
                dia.list_item_append(txt, device.icon, device=device)
            dia.list_go()

        def dia_canc_cb(dia):
            # events.listener_del('uit_storage')
            dia.delete()

        def dia_sel_cb(dia, device):
            print(device)
            txt = '<small>{}</>'.format(utf8_to_markup(str(device)))
            EmcDialog(style='info', title='Device info', text=txt)

        dia = EmcDialog(title='Storage devices', style='list',
                        done_cb=dia_sel_cb, canc_cb=dia_canc_cb)
        storage_events_cb('STORAGE_CHANGED')
        # events.listener_add('uit_storage', storage_events_cb)


class Test_Url(GenericItemClass):

    url1 = 'http://ipv4.download.thinkbroadband.com/5MB.zip'
    url2 = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/' \
           'resources/pdf/dummy.pdf'

    def __init__(self):
        super().__init__()
        self.dia = None
        self.dload = None

    def item_selected(self, url, user_data):
        self.dia = EmcDialog(style='progress', title=user_data,
                             text='Press start to test a 5MB download')
        self.dia.button_add('Close', lambda b: self.dia.delete())
        self.dia.button_add('delete()', lambda b: self.dload.delete())
        self.dia.button_add('To file (5M)', self.start_cb, self.url1)
        self.dia.button_add('To mem (13K)', self.start_cb, self.url2)

    def start_cb(self, btn, url):
        self.dia.text_set('Download started...')
        dest = '::tmp::' if url == self.url1 else '::mem::'
        self.dload = EmcUrl(url, dest=dest, done_cb=self.done_cb,
                            prog_cb=self.prog_cb, decode=None,
                            parent=self.dia)

    def done_cb(self, url, success, dest):
        print("DONE", success)
        if success and url.dest == '::mem::':
            size = len(dest)
            self.dia.text_set('Download successfully completed to Memory<br>'
                              'First bytes: {}<br>Download size: {} bytes'
                              .format(dest[:10], size))
        elif success and os.path.exists(dest):
            size = utils.hum_size(os.path.getsize(dest))
            self.dia.text_set('Download successfully completed to<br>{}<br>'
                              'File size: {} '.format(dest, size))
        else:
            self.dia.text_set("Error !!")

    def prog_cb(self, url, total, received):
        print("PROGRESS", url, total, received)
        self.dia.progress_set(received / total if total else 0)


class Test_Exe(GenericItemClass):

    path = os.path.dirname(__file__)
    infinite_path = os.path.join(path, 'infinite.py')

    def __init__(self):
        super().__init__()
        self.dia = None
        self.exe = None

    def item_selected(self, url, user_data):
        self.dia = EmcDialog(title='EmcExe test',
                             text='Press a button to run a command')
        self.dia.button_add('Close', lambda b: self.dia.delete())
        self.dia.button_add('delete()', lambda b: self.exe.delete())
        self.dia.button_add('"wrong"', self.run_btn_cb, ('wrong',))
        self.dia.button_add('"infinite.py"', self.run_btn_cb,
                            (sys.executable, self.infinite_path))
        self.dia.button_add('"ls -l"', self.run_btn_cb, ('ls', '-l'))
        self.dia.button_add('"ls"', self.run_btn_cb, ('ls',))

    def run_btn_cb(self, btn, pars):
        cmd = pars[0]
        params = pars[1:]
        self.exe = EmcExe(cmd, params, grab_output=True,
                          done_cb=self.exe_done_cb,
                          parent=self.dia,
                          asd1='asd_1', asd2='asd_2')
        self.dia.text_set('Running: "{} {}"<br><br>'
                          .format(cmd, ' '.join(params)))

    def exe_done_cb(self, exit_code, output, asd1, asd2):
        assert asd1 == 'asd_1'
        assert asd2 == 'asd_2'
        print("OUT", exit_code, output)
        self.dia.text_append('Process completed<br>'
                             'exit_code: {}<br>'
                             'output: {}'.format(exit_code, repr(output)))


class Test_CastPanel(GenericItemClass):
    def item_selected(self, url, user_data):
        CastPanel(name='Bruce Willis', lang='en')


class UiTestsModule(EmcModule):
    name = 'uitests'
    label = 'UI tests'
    icon = 'icon/star'
    info = 'This module serve as test for the various epymc components.'
    path = os.path.dirname(__file__)

    def __init__(self):
        DBG('__init__')
        mainmenu.item_add('uitests', 3, 'UI tests', self.icon, self.cb_mainmenu)
        self._browser = EmcBrowser('UI tests', 'List', self.icon)

        global _mod, _browser
        _mod = self
        _browser = self._browser

    def __shutdown__(self):
        mainmenu.item_del('uitests')
        self._browser.delete()

    def cb_mainmenu(self):
        # restore a previous browser state (if available)
        # if self._browser.freezed:
        #     self._browser.unfreeze()
        #     return
        #
        # self._browser.clear()
        self._browser.page_add('uitest://root', 'UI tests', None,
                               self.populate_root)
        # mainmenu.hide()
        self._browser.show()

    def populate_root(self, browser, url):

        browser.item_add(Test_Timer(), 'uitest://timer', 'EmcTimer')
        browser.item_add(Test_Idler(), 'uitest://idler', 'EmcIdler')
        browser.item_add(Test_Url(), 'uitest://download', 'EmcUrl')
        browser.item_add(Test_Exe(), 'uitest://exe', 'EmcExe')

        browser.item_add(Test_Dialog(), 'uitest://dialog', 'EmcDialog')
        browser.item_add(Test_Notify(), 'uitest://notify', 'EmcNotify')

        browser.item_add(Test_BG(), 'uitest://backdrop', 'Backdrop changer')

        browser.item_add(Test_Storage(), 'uitest://storage',
                                         'Storage Devices')
        browser.item_add(Test_FolderSelector(), 'uitest://fselector',
                                                'Folder Selector')
        browser.item_add(Test_SourceManager(), 'uitest://srcmngr',
                                               'Source Manager')
        browser.item_add(Test_CastPanel(), 'uitest://tmdb',
                                           'TMDB CastPanel')

        browser.item_add(Test_Browser(), 'uitest://browser', 'EmcBrowser')
        browser.item_add(Test_ImageDialog(), 'uitest://imgd',
                         'EmcImage in Dialog')
        browser.item_add(Test_ImageBrowser(), 'uitest://imgb',
                         'EmcImage in Browser')

        browser.item_add(Test_MediaPlayer(), 'uitest://mpv',
                         'MediaPlayer - Local video')
        browser.item_add(Test_MediaPlayer(), 'uitest://mpvo',
                         'Mediaplayer - Online Video (good)')
        browser.item_add(Test_MediaPlayer(), 'uitest://mpvob',
                         'Mediaplayer - Online Video (bad video)')
        browser.item_add(Test_MediaPlayer(), 'uitest://dvd',
                         'Mediaplayer - DVD Playback (/dev/cdrom) **TODO**')

        # browser.item_add(Test_Buttons(), 'uitest://buttons', 'Buttons + Focus')
        # browser.item_add(Test_Focus(), 'uitest://focus_1', 'Focus corner case 1')
        # browser.item_add(MainPageItemClass(), 'uitest://focus_2', 'Focus corner case 2')
        # browser.item_add(MainPageItemClass(), 'uitest://focus_3', 'Focus corner case 3')

        # browser.item_add(MainPageItemClass(), 'uitest://mbrainz', 'Music Brainz AudioCD (/dev/cdrom)')
        # browser.item_add(MainPageItemClass(), 'uitest://menu', 'Menu small (dismiss on select)')
        # browser.item_add(MainPageItemClass(), 'uitest://menu_long', 'Menu long (no dismiss on select)')
        # browser.item_add(MainPageItemClass(), 'uitest://sliders', 'Sliders')
        # browser.item_add(MainPageItemClass(), 'uitest://vkbd', 'Virtual Keyboard')
        # browser.item_add(MainPageItemClass(), 'uitest://encoding', 'Various string encoding tests')

        # browser.item_add(MainPageItemClass(), 'uitest://movies_name', 'Movies name test')
        # browser.item_add(MainPageItemClass(), 'uitest://sniffer', 'Event Sniffer')
        # browser.item_add(MainPageItemClass(), 'uitest://ev_emit', 'Event Emit')
        # browser.item_add(MainPageItemClass(), 'uitest://icons', 'Icons gallery')
        # browser.item_add(MainPageItemClass(), 'uitest://imagegal', 'Images gallery')
        # browser.item_add(Test_Styles(), 'uitest://styles', 'Text styles')
        # browser.item_add(MainPageItemClass(), 'uitest://dm', 'Download Manager - start')
        # browser.item_add(MainPageItemClass(), 'uitest://dm2', 'Download Manager - show')
        # browser.item_add(MainPageItemClass(), 'uitest://tmdb', 'Themoviedb.org query with gui')

        # browser.item_add(MainPageItemClass(), 'uitest://brdump', 'Dump Browser pages')

    # def populate_encoding_page(self, browser, url):
    #     _mod._browser.item_add(EncodingItemClass(), 'test1', 'Test 1: tmdb.org json parser')
    #     _mod._browser.item_add(EncodingItemClass(), 'test2', 'Test 2: tmdb.org url encode')
    #     _mod._browser.item_add(EncodingItemClass(), 'test3', 'Test 3: tmdb.org virtual keyboard')



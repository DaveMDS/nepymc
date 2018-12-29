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
import pprint

from nepymc.modules import EmcModule
from nepymc import mainmenu
from nepymc import mediaplayer
from nepymc.mainloop import EmcTimer
from nepymc.browser import EmcBrowser, \
    EmcItemClass, BackItemClass, FolderItemClass
from nepymc.gui import EmcDialog
# from epymc.gui import EmcDialog, EmcVKeyboard, EmcFolderSelector, \
#    EmcButton, EmcNotify, EmcMenu, DownloadManager, EmcSlider

# import epymc.utils as utils
# import epymc.events as events
# import epymc.ini as ini
# import epymc.storage as storage
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
class ImagesItemClass(EmcItemClass):
   path = os.path.dirname(__file__)

   def label_get(self, url, user_data):
      return(user_data)

   def icon_get(self, url, user_data):
      if url == 'special_icon':
         return 'icon/home'

   def poster_get(self, url, user_data):
      if url == 'local_path':
         return os.path.join(self.path, 'menu_bg.png')
      elif url == 'remote_url':
         return 'https://image.tmdb.org/t/p/original/3bKHPDte16BeNLo57W2FwO0jRJZ.jpg', '/tmp/asdasdas'
      elif url == 'remote_url_cache':
         return 'https://image.tmdb.org/t/p/original/cUKn61e7bUUglIGNGBEtzyuCDR4.jpg'
      elif url == 'special_bd':
         return 'special/bd/My super cool movie without a poster'
      elif url == 'special_cd':
         return 'special/cd/My album without a cover'
      elif url == 'special_folder':
         return 'special/folder/This is my special/folder/name <br>' \
                '(can also include "/" and other special chars)<br>' \
                'àèìòù<br>నాన్నకు ప్రేమతో<br>もののけ姫<br><br>...and tags:<br>' \
                + TEST_STYLE
      elif url == 'special_null':
         return None
      #TODO failure for local and remote

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

      elif url == 'uitest://images':
         _mod._browser.page_add('uitest://images', 'Image tests',
                                ('List', 'PosterGrid'),
                                _mod.populate_image_page)

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

      # Notify
      elif url == 'uitest://notify':
         EmcNotify('<title>Title 1</><br>' \
             'Without icon.<br>' \
             'Will hide in 10 seconds.',
              hidein=20)
         EmcNotify('<title>Title 2</><br>' \
             'This one with an image.',
              icon = 'dvd_cover_blank.png')
         EmcNotify('<title>Title 3</><br>' \
             'This one with an icon',
              icon = 'icon/movie')
         EmcNotify('<title>Title 4</><br>' \
             'Test longer text and tags.<br>' \
             '<b>bold</b> <i>italic</i> <u>underline</u> <link>link</link> ' \
             '<info>info</info> <success>success</success> ' \
             '<warning>warning</warning> <failure>failure</failure>.',
              icon = 'icon/movie')

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

      # Source Selector
      elif url == 'uitest://sselector':
         EmcFolderSelector(title='Folder Selector Test',
                           done_cb=lambda p: DBG('Selected: ' + p))

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

      # Storage devices
      elif url == 'uitest://storage':

         def storage_events_cb(event):
            if event != 'STORAGE_CHANGED':
               return
            dia.list_clear()
            for device in storage.list_devices():
               txt = '{0.label} [ {0.device} ➙ {0.mount_point} ]'.format(device)
               dia.list_item_append(txt, device.icon, device=device)
            dia.list_go()

         def dia_canc_cb(dia):
            events.listener_del('uit_storage')
            dia.delete()

         def dia_sel_cb(dia, device):
            print(device)
            txt = '<small>{}</>'.format(utf8_to_markup(str(device)))
            EmcDialog(style='info', title='Device info', text=txt)

         dia = EmcDialog(title='Storage devices', style='list',
                         done_cb=dia_sel_cb, canc_cb=dia_canc_cb)
         storage_events_cb('STORAGE_CHANGED')
         events.listener_add('uit_storage', storage_events_cb)

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
        self.dialog = dia = EmcDialog('EmcTimer test', 'Press "create"')
        dia.button_add('Create oneshot', self.timer_create_oneshot)
        dia.button_add('Create onstart', self.timer_create_onstart)
        dia.button_add('reset()', lambda: self.timer.reset())
        dia.button_add('start()', lambda: self.timer.start())
        dia.button_add('stop()', lambda: self.timer.stop())
        dia.button_add('destroy()', lambda: self.timer.delete())
        dia.button_add('Close test', self.close_test)

    def timer_create_oneshot(self):
        self.iter_count = 0
        self.timer = EmcTimer(1000, self.timer_cb, oneshot=True, key1="V1", key2="V2")

    def timer_create_onstart(self):
        self.iter_count = 0
        self.timer = EmcTimer(1000, self.timer_cb, onstart=True)

    def timer_cb(self, key1=None, key2=None):
        self.iter_count += 1
        self.dialog.text_set("Triggered: %d<br>key1=%s key2=%s" % (
                             self.iter_count, key1, key2))

    def close_test(self):
        self.timer.delete()
        self.dialog.delete()


class Test_MediaPlayer(GenericItemClass):
    def item_selected(self, url, user_data):
        print("M P ", url, user_data)

        # Mediaplayer Local Video
        if url == 'uitest://mpv':
            f = os.path.expanduser('~/Video/testvideo.avi')
            # f = os.path.expanduser('~/Video/testvideo.mp4')
            mediaplayer.play_url(f)  # , start_from=0)
            mediaplayer.title_set('Testing title')
            mediaplayer.poster_set('image/dvd_cover_blank.png')

        # Mediaplayer Online Video (good)
        elif url == 'uitest://mpvo':
            pass
            # mediaplayer.play_url('http://trailers.apple.com/movies/independent/airracers/airracers-tlr1_h480p.mov')
            # http://samples.mplayerhq.hu/
            # http://download.wavetlan.com/SVV/Media/HTTP/http-mp4.htm

        # Mediaplayer Online Video (med)
        elif url == 'uitest://mpvom':
            mediaplayer.play_url('http://fredrik.hubbe.net/plugger/xvidtest.avi')

        # Mediaplayer Online Video (bad)
        elif url == 'uitest://mpvob':
            mediaplayer.play_url(
                'http://www.archive.org/download/TheMakingOfSuzanneVegasSecondLifeGuitar/3-TheMakingOfSuzanneVega_sSecondLifeGuitar.mp4')

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


class Test_Dialog(GenericItemClass):

    def populate_subpage(self, browser, url):
        browser.item_add(self, url + '/info', 'Dialog - Info')
        browser.item_add(self, url + '/warning', 'Dialog - Warning')
        browser.item_add(self, url + '/warning2', 'Dialog - Warning (no title)')
        browser.item_add(self, url + '/error', 'Dialog - Error')
        browser.item_add(self, url + '/yesno', 'Dialog - YesNo')
        browser.item_add(self, url + '/cancel', 'Dialog - Cancel')
        browser.item_add(self, url + '/progress', 'Dialog - Progress  **TODO**')
        browser.item_add(self, url + '/progress-btn', 'Dialog - Progress + buttons  **TODO**')
        browser.item_add(self, url + '/list', 'Dialog - List  **TODO**')
        browser.item_add(self, url + '/list-btn', 'Dialog - List with buttons  **TODO**')
        browser.item_add(self, url + '/panel1', 'Dialog - Panel full')
        browser.item_add(self, url + '/panel4', 'Dialog - Panel full more')
        browser.item_add(self, url + '/panel2', 'Dialog - Panel no buttons ')
        browser.item_add(self, url + '/panel3', 'Dialog - Panel no title')
        browser.item_add(self, url + '/buffering', 'Dialog - Buffering  **TODO**')

    def item_selected(self, url, user_data):
        # main item selected, create the subpage
        if url == 'uitest://dialog':
            _browser.page_add(url, user_data, None, self.populate_subpage)

        # Dialog - Info
        elif url.endswith('/info'):
            print("DIALOG INFO", url, user_data)
            # EmcDialog(title='Dialog - Info', text=LOREM, style='info')
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

        # Dialog - Error **
        elif url.endswith('/error'):
            text = 'This is an <br><br><b>Error</><br>dialog<br>'
            EmcDialog(title='Dialog - Error', text=text, style='error')

        # Dialog - YesNo
        elif url.endswith('/yesno'):
            text = 'This is an <br><br><b>Yes/No</><br>dialog<br>'
            EmcDialog(title='Dialog - YesNo', text=text, style='yesno',
                               done_cb=lambda btn: DBG('done'))

        # Dialog - Cancel
        elif url.endswith('/cancel'):
            text = 'This is an <br><br><b>Cancel operation</><br>dialog<br>'
            EmcDialog(title='Dialog - Cancel', text=text,
                      style='cancel', spinner=True)

        # Dialog - Progress ** TODO **
        elif url.startswith('uitest://dialog/progress'):
            def _canc_cb(dialog):
                t.delete()
                d.delete()

            def _progress_timer():
                d.progress_set(self._progress)
                self._progress += 0.01
                if self._progress > 1:
                    self._progress = 0;
                return True # renew the callback

            text = 'This is a <br><br><b>Progress operation</><br>dialog<br>'
            d = EmcDialog(title='Dialog - Progress', text=text,
                          style='progress', done_cb=_canc_cb,
                          canc_cb=_canc_cb)
            if url.endswith('btn'):
                d.button_add("btn1", selected_cb=lambda b: print('btn1 callback'))
                d.button_add("btn2", selected_cb=lambda b: print('btn2 callback'))
                d.button_add("btn3", selected_cb=lambda b: print('btn3 callback'))
            self._progress = 0.0
            t = ecore.Timer(0.2, _progress_timer)

        # Dialog - List ** TODO **
        elif url.endswith('/list'):
            def _dia_list_cb(dia):
                item = dia.list_item_selected_get()
                print('Selected: ' + str(item))
                # dia.delete()
            d = EmcDialog(title='Dialog - List', style='list',
                          done_cb=_dia_list_cb)
            d.list_item_append('item 1', 'icon/home')
            d.list_item_append('item 2', 'icon/star', 'icon/check_on')
            d.list_item_append('item 3 <b>bold</> <info>info</> <success>success</> <failure>failure</> <i>etc...</>',
                               'icon/star', 'icon/check_on')
            d.list_item_append('item 4', 'icon/tag', 'text/End Text')
            d.list_item_append('item 5', 'icon/tag', 'text/<b>End</> <info>Text</>')
            for i in range(6, 101):
                d.list_item_append('item %d'%i)
            d.list_go()

        # Dialog - List with buttons ** TODO **
        elif url.endswith('/list-btn'):
            d = EmcDialog(title='Dialog - List with buttons',
                          style='list')
            for i in range(1, 40):
                d.list_item_append('item %d'%i)
            d.button_add('One', selected_cb=lambda b: print('btn1 callback'))
            d.button_add('Two', selected_cb=lambda b: print('btn2 callback'))
            d.button_add('Tree', selected_cb=lambda b: print('btn3 callback'))
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
            ecore.Timer(0.2, _progress_timer2)


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
        browser.item_add(Test_Browser(), 'uitest://browser', 'EmcBrowser')
        browser.item_add(Test_Dialog(), 'uitest://dialog', 'EmcDialog')

        browser.item_add(Test_MediaPlayer(), 'uitest://mpv',
                         'MediaPlayer - Local video')
        browser.item_add(Test_MediaPlayer(), 'uitest://mpvo',
                         'Mediaplayer - Online Video (good)')
        browser.item_add(Test_MediaPlayer(), 'uitest://mpvom',
                         'Mediaplayer - Online Video (med)')
        browser.item_add(Test_MediaPlayer(), 'uitest://mpvob',
                         'Mediaplayer - Online Video (bad video)')
        browser.item_add(Test_MediaPlayer(), 'uitest://dvd',
                         'Mediaplayer - DVD Playback (/dev/cdrom)')

        # browser.item_add(Test_Buttons(), 'uitest://buttons', 'Buttons + Focus')
        # browser.item_add(Test_Focus(), 'uitest://focus_1', 'Focus corner case 1')
        # browser.item_add(MainPageItemClass(), 'uitest://focus_2', 'Focus corner case 2')
        # browser.item_add(MainPageItemClass(), 'uitest://focus_3', 'Focus corner case 3')
        # browser.item_add(MainPageItemClass(), 'uitest://storage', 'Storage devices')
        # browser.item_add(MainPageItemClass(), 'uitest://sselector', 'Folder Selector')
        # browser.item_add(MainPageItemClass(), 'uitest://mbrainz', 'Music Brainz AudioCD (/dev/cdrom)')
        # browser.item_add(MainPageItemClass(), 'uitest://menu', 'Menu small (dismiss on select)')
        # browser.item_add(MainPageItemClass(), 'uitest://menu_long', 'Menu long (no dismiss on select)')
        # browser.item_add(MainPageItemClass(), 'uitest://sliders', 'Sliders')
        # browser.item_add(MainPageItemClass(), 'uitest://vkbd', 'Virtual Keyboard')
        # browser.item_add(MainPageItemClass(), 'uitest://encoding', 'Various string encoding tests')

        # browser.item_add(MainPageItemClass(), 'uitest://images', 'Browser + EmcImage')
        # browser.item_add(MainPageItemClass(), 'uitest://movies_name', 'Movies name test')
        # browser.item_add(MainPageItemClass(), 'uitest://sniffer', 'Event Sniffer')
        # browser.item_add(MainPageItemClass(), 'uitest://ev_emit', 'Event Emit')
        # browser.item_add(MainPageItemClass(), 'uitest://notify', 'Notify Stack')
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

    # def populate_image_page(self, browser, url):
    #     _mod._browser.item_add(ImagesItemClass(), 'local_path', 'From a local path')
    #     _mod._browser.item_add(ImagesItemClass(), 'remote_url', 'From a remote url (with local dest)')
    #     _mod._browser.item_add(ImagesItemClass(), 'remote_url_cache', 'From a remote url (with auto cache)')
    #     _mod._browser.item_add(ImagesItemClass(), 'special_folder', 'Special Folder')
    #     _mod._browser.item_add(ImagesItemClass(), 'special_bd', 'Special Blu-ray')
    #     _mod._browser.item_add(ImagesItemClass(), 'special_cd', 'Special Compact-disk')
    #     _mod._browser.item_add(ImagesItemClass(), 'special_icon', 'Special Icon (in PosterGrid view)')
    #     _mod._browser.item_add(ImagesItemClass(), 'special_null', 'Special Null (transparent)')


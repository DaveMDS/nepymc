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
# import random
# from datetime import datetime
from collections import namedtuple
from typing import List

from nepymc import utils
from nepymc import ini
from nepymc.gui import EmcGui, EmcDialog, EmcVideoPlayer
from nepymc.sdb import EmcDatabase
from nepymc import input_events
# from nepymc import events
# from nepymc.gui import EmcDialog, EmcButton, EmcMenu, DownloadManager, \
#    EmcNotify, EmcImage, EmcSlider
# from nepymc.subtitles import Subtitles, Opensubtitles


def LOG(*args):
    print('MEDIAPLAYER:', *args)


def DBG(*args):
    print('MEDIAPLAYER:', *args)
    pass


video_extensions = [
    '.avi', '.mpg', '.mpeg', '.mpe', '.ogv', '.mkv', '.divx', '.xvid', '.mp4',
    '.wmv', '.flv', '.f4v', '.mov', '.m4v', '.m2v', '.mp4v', '.mpeg4', '.dv',
    '.rv', '.webm', '.vid', '.h264', '.rm'
]
audio_extensions = ['.mp3', '.ogg', '.oga', '.flac', '.m4a', '.wav', '.opus']


MediaTrack = namedtuple('MediaTrack', 'idx lang name codec active')


_volume = 0.0  # Linear volume between 0 and MAX (100 by default)
_volume_muted = False
_player: EmcVideoPlayer | None = None  # EmcVideoPlayer or EmcAudioPlayer instance, or None
_saved_player = None  # EmcAudioPlayer while EmcVideoPlayer is active
_onair_url = None
_onair_title = None
_onair_poster = None
_play_db = None  # key: url  data: {'started': 14, 'finished': 0, 'stop_at': 0 }


#
# ---- module API ----
#

def init():
    global _volume
    global _play_db
    global video_extensions
    global audio_extensions

    # default config values
    ini.add_section('mediaplayer')
    ini.get('mediaplayer', 'volume', '75')
    ini.get('mediaplayer', 'resume_from_last_pos', '0')
    ini.get('mediaplayer', 'playlist_loop', 'False')
    ini.get('mediaplayer', 'playlist_shuffle', 'False')
    ini.get('mediaplayer', 'video_extensions', '')
    ini.get('mediaplayer', 'audio_extensions', '')
    ini.get('mediaplayer', 'volume_adjust_step', '3')
    ini.get('mediaplayer', 'volume_exponent', '2')
    ini.get('mediaplayer', 'volume_maximum', '100')
    ini.add_section('subtitles')
    ini.get('subtitles', 'langs', 'en')
    ini.get('subtitles', 'encoding', 'latin_1')
    ini.get('subtitles', 'always_try_utf8', 'True')
    ini.get('subtitles', 'opensubtitles_user', '')
    ini.get('subtitles', 'opensubtitles_pass', '')

    audio_extensions += ini.get_string_list('mediaplayer', 'audio_extensions')
    video_extensions += ini.get_string_list('mediaplayer', 'video_extensions')

    # restore volume from previous session
    _volume = ini.get_float('mediaplayer', 'volume')

    # simple db to store the count of played files
    _play_db = EmcDatabase('playcount')

    # input events
    input_events.listener_add("mediaplayer", _input_event_cb)


def shutdown():
    input_events.listener_del("mediaplayer")

    if _player:
        _player.delete()
    if _saved_player:
        _saved_player.delete()

    global _play_db
    del _play_db


#
# ---- mediaplyer API ----
#

def play_url(url, only_audio=False, start_from=None):
    global _onair_url, _onair_title, _onair_poster
    global _player, _saved_player

    # default to 'file://' if not given
    if url.find('://', 2, 15) is -1:
        url = 'file://' + url

    # check url
    if url.startswith('file://') and not os.path.exists(url[7:]):
        text = '<b>%s:</b><br>%s' % (_('File not found'), url)
        EmcDialog(text=text, style='error')
        return

    DBG('play_url: %s' % url)
    _onair_url = url
    _onair_title = None
    _onair_poster = None

    if only_audio:
        _play_real(start_from, only_audio)
        return

    # save (pause and hide) the AudioPlayer if it's active
    # if isinstance(_player, EmcAudioPlayer):
    #     _player.pause()
    #     _player.hide()
    #     _saved_player = _player
    #     _player = None

    # starting position forced by param
    if start_from is not None:
        _play_real(start_from, only_audio)
        return

    # dont resume on dvd playback, it doesn't work :(
    if url.startswith('dvd://'):
        _play_real(0)
        return

    # resume playback from last position ?
    #   0=ask, 1=always, 2=never
    resume_opt = ini.get_int('mediaplayer', 'resume_from_last_pos')

    if resume_opt == 2:  # never resume
        _play_real(0)
        return

    counts = play_counts_get(url)
    pos = counts['stop_at'] or 0

    if resume_opt == 1:  # always resume
        _play_real(pos)
        return

    if pos < 10000:  # don't ask if less then 10 seconds
        _play_real(0)
        return

    # ask the user if resume or not
    time = utils.millis_to_duration(pos, True)
    EmcDialog(style='yesno', title=_('Resume playback'),
              text=_('Continue from %s ?') % time,
              done_cb=_resume_yes_cb, canc_cb=_resume_no_cb,
              user_data=pos)


def _resume_yes_cb(dia):
    dia.delete()
    _play_real(start_from=dia.data_get())


def _resume_no_cb(dia):
    dia.delete()
    _play_real(0)


def _play_real(start_from=None, only_audio=False):
    global _player

    url = _onair_url

    if only_audio:
        if _player is None:
            _player = EmcAudioPlayer()
        _player.url = url
    else:
        if _player is None:
            _player = EmcVideoPlayer()
        _player.url = url
        _player.position = start_from or 0
        _player.volume_set(volume_adjusted_get())
        # _player.active_subtitle_track = -1
        _player.poster_set(_onair_poster)
        _player.title_set(_onair_title)
        _player.play()

        # keep the counts of played/finished urls
        if _play_db.id_exists(url):
            counts = _play_db.get_data(url)
            counts['started'] += 1
            _play_db.set_data(url, counts)
        else:
            counts = {'started': 0, 'finished': 0, 'stop_at': 0}
            _play_db.set_data(url, counts)


def poster_set(poster):
    global _onair_poster

    _onair_poster = poster
    if _player:
        _player.poster_set(poster)


def title_set(title):
    global _onair_title

    _onair_title = title
    if _player:
        _player.title_set(title)


def play_counts_get(url):
    try:
        return _play_db.get_data(url)
    except KeyError:
        return {'started': 0,  # num times started
                'finished': 0,  # num times finished
                'stop_at': 0}  # last play pos


def stop(emit_playback_finished=False):
    global _player, _saved_player, _onair_url, _onair_title

    DBG('Stop()')

    # update play counts (only for videos)
    if isinstance(_player, EmcVideoPlayer):
        counts = play_counts_get(_onair_url)
        if position_percent_get() >= 0.99:  # 1% from the end
            counts['finished'] += 1
            counts['stop_at'] = 0
        else:
            counts['stop_at'] = _player.position
        _play_db.set_data(_onair_url, counts)

    # notify
    # if emit_playback_finished:
    #     events.event_emit('PLAYBACK_FINISHED')

    # stop the player
    if _player:
        _player.stop()
        _player = None

    # restore a saved AudioPlayer
    if _saved_player is not None:
        _player = _saved_player
        _player.show()
        _saved_player = None
    else:
        # playlist.clear()
        _onair_url = None
        _onair_title = None


def pause():
    if _player:
        _player.pause()


def play():
    if _player:
        _player.play()


# def pause_toggle():
#     if _player:
#         _player.pause_toggle()
#
#
# def play_state_get():
#     """ 'Stopped', 'Paused' or 'Playing' (as per mpris spec, do not change!) """
#     if _player is None:
#         return 'Stopped'
#     if _player.paused:
#         return 'Paused'
#     return 'Playing'


def seek(offset: int):
    """ change player position relative, offset in millis """
    if _player:
        position_set(_player.position + offset)


def forward():
    if _player:
        position_set(position_get() + 10 * 1000)


def backward():
    if _player:
        position_set(position_get() - 10 * 1000)


def fforward():
    if _player:
        position_set(position_get() + 60 * 1000)


def fbackward():
    if _player:
        position_set(position_get() - 60 * 1000)

#
#
# def seekable_get():
#     return _player.seekable if _player else False
#


def position_set(pos: int):
    """ set player position in milliseconds from the start """
    if _player:
        _player.position = utils.clamp(pos, 0, _player.duration)


def position_percent_set(val):
    """ set the playback position in the range 0.0 -> 1.0 """
    if _player:
        position_set(_player.duration * val)


def position_get() -> int:
    """ get player position in milliseconds from the start """
    return _player.position if _player else 0


def position_percent_get() -> float:
    """ return the playback position in the range 0.0 -> 1.0 """
    if _player:
        pos, dur = _player.position, _player.duration
        return (pos / dur) if dur > 0 else 0.0
    else:
        return 0.0


def duration_get() -> int:
    """ return the currently playing media duration in millis """
    if _player:
        return _player.duration


def volume_set(vol: float) -> None:
    """ Set linear volume. Float, always between 0 and 100 """
    global _volume

    vol = utils.clamp(vol, 0, 100)
    vol = vol / 100.0 * ini.get_int('mediaplayer', 'volume_maximum')

    if vol == _volume:
        return

    _volume = vol
    EmcGui.instance().volume_set(vol)
    ini.set('mediaplayer', 'volume', _volume)
    # events.event_emit('VOLUME_CHANGED')

    if _player:
        _player.volume_set(volume_adjusted_get())


def volume_get():
    """ get linear volume. Float, always between 0 and 100 """
    maximum = ini.get_int('mediaplayer', 'volume_maximum')
    return _volume / maximum * 100.0


def volume_adjusted_get():
    """ logarithmic adjusted volume. Float, between 0.0 and MAX (100 by default)
          https://www.dr-lex.be/info-stuff/volumecontrols.html
    """
    exp = ini.get_int('mediaplayer', 'volume_exponent')
    if 1 < exp < 5:
        adjusted = ((_volume / 100.0) ** exp) * 100
    else:
        adjusted = _volume

    return adjusted


def volume_step_get():
    """ volume adjustament step. Int, between 1 and 100 """
    return ini.get_int('mediaplayer', 'volume_adjust_step')


def volume_inc():
    volume_set(volume_get() + volume_step_get())


def volume_dec():
    volume_set(volume_get() - volume_step_get())


def volume_mute_set(mute):
    global _volume_muted

    _volume_muted = bool(mute)
    if _player:
        _player.volume_mute_set(_volume_muted)
#     events.event_emit('VOLUME_CHANGED')


def volume_mute_get():
    return _volume_muted


def volume_mute_toggle():
    volume_mute_set(not _volume_muted)


def audio_tracks_get() -> List[MediaTrack]:
    return _player.audio_tracks if _player else []


def audio_track_get() -> int:
    return _player.active_audio_track if _player else -1


def audio_track_set(idx: int):
    if _player:
        _player.active_audio_track = idx


def video_tracks_get() -> List[MediaTrack]:
    return _player.video_tracks if _player else []


def video_track_get() -> int:
    return _player.active_video_track if _player else -1


def video_track_set(idx: int):
    if _player:
        _player.active_video_track = idx


def subtitle_tracks_get() -> List[MediaTrack]:
    return _player.subtitle_tracks if _player else []


def subtitle_track_get() -> int:
    return _player.active_subtitle_track if _player else -1


def subtitle_track_set(idx: int):
    if _player:
        _player.active_subtitle_track = idx


# ---- input events ----
def _input_event_cb(event):
    if event == 'VOLUME_UP':
        volume_inc()
    elif event == 'VOLUME_DOWN':
        volume_dec()
    elif event == 'VOLUME_MUTE':
        # volume_mute_toggle()
        print('mute toggle')
    else:
        return input_events.EVENT_CONTINUE
    return input_events.EVENT_BLOCK


###############################################################################
"""
class EmcPlayerBase_OLD_OLD_OLD_(object):
    def __init__(self):
        self._url = None

        ### listen to input and generic events
        # input_events.listener_add(self.__class__.__name__ + 'Base',
        #                           self._base_input_events_cb)
        # events.listener_add(self.__class__.__name__ + 'Base',
        #                     self._base_events_cb)

    def delete(self):
        # input_events.listener_del(self.__class__.__name__ + 'Base')
        # events.listener_del(self.__class__.__name__ + 'Base')
        raise NotImplementedError

    def video_object_get(self):
        # return self._emotion
        raise NotImplementedError

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        # default to 'file://' if not given
        if url.find('://', 2, 15) == -1:
            url = 'file://' + url
        self._url = url

        # Do not pass "file://" to emotion. Vlc has a bug somewhere that prevent
        # files with special chars in them to play (the bug don't appear if no
        # "file://" is given. The bug can be seen also using normal vlc from
        # the command line.
        self._emotion.file_set(url[7:] if url.startswith('file://') else url)
        self._emotion.play = True
        self._emotion.audio_volume = volume_adjusted_get() / 100.0
        self._emotion.audio_mute = volume_mute_get()
        if not url.startswith('dvd://'):  # spu used in dvdnav
            self._emotion.spu_mute = True
            self._emotion.spu_channel = -1

    @property
    def seekable(self):
        return self._emotion.seekable

    @property
    def play_length(self):
        return self._emotion.play_length

    @property
    def position(self):
        "" the playback position in seconds (float) from the start ""
        return self._emotion.position

    @position.setter
    def position(self, pos):
        self._emotion.position = pos
        events.event_emit('PLAYBACK_SEEKED')

    @property
    def position_percent(self):
        "" the playback position in the range 0.0 -> 1.0 ""
        pos, len = self.position, self.play_length
        return (pos / len) if len > 0 else 0.0

    @position_percent.setter
    def position_percent(self, val):
        self.position = self.play_length * val

    def seek(self, offset):
        "" offset in seconds (float) "" 
        newpos = self.position + offset
        self.position = max(0.0, newpos)

    def forward(self):
        self.seek(+10)

    def backward(self):
        self.seek(-10)

    def fforward(self):
        self.seek(+60)

    def fbackward(self):
        self.seek(-60)

    @property
    def paused(self):
        return not self._emotion.play

    def pause(self):
        self._emotion.play = False
        events.event_emit('PLAYBACK_PAUSED')

    def unpause(self):
        self._emotion.play = True
        events.event_emit('PLAYBACK_UNPAUSED')

    def pause_toggle(self):
        self.unpause() if self.paused else self.pause()

    @property
    def volume(self):
        return int(self._emotion.audio_volume * 100)

    @volume.setter
    def volume(self, value):
        self._emotion.audio_volume = float(value) / 100

    @property
    def muted(self):
        return self._emotion.audio_mute

    @muted.setter
    def muted(self, value):
        self._emotion.audio_mute = bool(value)

    @property
    def buffer_size(self):
        return self._emotion.buffer_size

    @buffer_size.setter
    def buffer_size(self, value):
        self._emotion.buffer_size = value

    @property
    def audio_tracks(self):
        " list of (index, lang, name, codec, active) "
        Track = namedtuple('Track', 'idx lang name codec active')
        current = self._emotion.audio_channel
        count = self._emotion.audio_channel_count()
        return [Track(i, None, self._emotion.audio_channel_name_get(i),
                      None, i == current)
                for i in range(count)]

    @property
    def selected_audio_track(self):
        " index of the selected audio track "
        return self._emotion.audio_channel

    @selected_audio_track.setter
    def selected_audio_track(self, index):
        index = max(0, min(index, self._emotion.audio_channel_count()))
        self._emotion.audio_channel = index

    @property
    def video_tracks(self):
        " list of (index, lang, name, codec, active) "
        Track = namedtuple('Track', 'idx lang name codec active')
        current = self._emotion.video_channel
        count = self._emotion.video_channel_count()
        return [Track(i, None, self._emotion.video_channel_name_get(i),
                      None, i == current)
                for i in range(count)]

    @property
    def selected_video_track(self):
        " index of the selected video track "
        return self._emotion.video_channel

    @selected_video_track.setter
    def selected_video_track(self, index):
        index = max(0, min(index, self._emotion.video_channel_count()))
        self._emotion.video_channel = index

    ### emotion obj callbacks (implemented in subclasses)
    def _playback_started_cb(self, vid):
        pass

    def _playback_finished_cb(self, vid):
        pass

    ### events
    def _base_input_events_cb(self, event):
        if event == 'PLAY':
            self.unpause()
            return input_events.EVENT_BLOCK

        elif event == 'TOGGLE_PAUSE':
            self.pause_toggle()
            return input_events.EVENT_BLOCK

        elif event == 'PAUSE':
            self.pause()
            return input_events.EVENT_BLOCK

        elif event == 'STOP':
            stop(True)
            return input_events.EVENT_BLOCK

        elif event == 'FORWARD':
            self.forward()
            return input_events.EVENT_BLOCK

        elif event == 'BACKWARD':
            self.backward()
            return input_events.EVENT_BLOCK

        elif event == 'FAST_FORWARD':
            self.fforward()
            return input_events.EVENT_BLOCK

        elif event == 'FAST_BACKWARD':
            self.fbackward()
            return input_events.EVENT_BLOCK

        return input_events.EVENT_CONTINUE

    def _base_events_cb(self, event):
        if event == 'VOLUME_CHANGED':
            self.volume = volume_adjusted_get()
            self.muted = volume_mute_get()
"""

"""
###############################################################################
class EmcAudioPlayer(gui.EmcLayout, EmcPlayerBase):
    def __init__(self, url=None):
        self._controls_visible = False
        self._slider_timer = None

        ### init the layout
        gui.EmcLayout.__init__(self, gui.layout, name='AudioPlayer',
                               is_focus_manager=True, focus_history_allow=False,
                               file=(gui.theme_file, 'emc/audioplayer/default'))
        self.signal_callback_add('audioplayer,expand,request', '',
                                 lambda a, s, d: self.controls_show())
        self.signal_callback_add('audioplayer,contract,request', '',
                                 lambda a, s, d: self.controls_hide())
        self.callback_focused_add(self._focused_cb)

        ### setup the playlist
        playlist.loop = ini.get_bool('mediaplayer', 'playlist_loop')
        playlist.shuffle = ini.get_bool('mediaplayer', 'playlist_shuffle')

        ### init the base player class
        EmcPlayerBase.__init__(self)
        self.url = url

        ### control buttons
        self.box_append('buttons.box', EmcButton(self, icon='icon/prev',
                                                 cb=lambda
                                                     b: input_events.event_emit(
                                                     'PLAYLIST_PREV')))
        self.box_append('buttons.box', EmcButton(self, icon='icon/pause',
                                                 cb=lambda
                                                     b: input_events.event_emit(
                                                     'TOGGLE_PAUSE'),
                                                 name='PlayPauseBtn'))
        self.box_append('buttons.box', EmcButton(self, icon='icon/next',
                                                 cb=lambda
                                                     b: input_events.event_emit(
                                                     'PLAYLIST_NEXT')))
        self.box_append('buttons.box', EmcButton(self, icon='icon/stop',
                                                 cb=lambda
                                                     b: input_events.event_emit(
                                                     'STOP')))
        b = EmcButton(self, icon='icon/loop', toggle=True,
                      cb=self._toggle_loop_cb)
        b.toggled = playlist.loop
        self.box_append('buttons.box', b)
        b = EmcButton(self, icon='icon/shuffle', toggle=True,
                      cb=self._toggle_shuffle_cb)
        b.toggled = playlist.shuffle
        self.box_append('buttons.box', b)
        self.box_append('buttons.box', EmcButton(self, _('Playlist'), icon=None,
                                                 cb=lambda b: PlayListEditor()))

        ### volume slider
        self._vol_slider = EmcSlider(self, indicator_show=False)
        self._vol_slider.content_set('end', gui.load_icon('icon/volume'))
        self._vol_slider.callback_changed_add(self._vol_slider_changed_cb)
        self.content_set('vol.slider', self._vol_slider)
        self._vol_slider.step = volume_step_get() / 100.0
        self._vol_slider.value = volume_get() / 100.0

        ### position slider
        self._pos_slider = EmcSlider(self, indicator_show_on_focus=True)
        self._pos_slider.callback_changed_add(self._pos_slider_changed_cb)
        self.content_set('pos.slider', self._pos_slider)

        ### playlist genlist
        self._itc = elm.GenlistItemClass(item_style='default',
                                         text_get_func=self._gl_text_get)
        self._gl = gui.EmcGenlist(self, style='playlist', name='AudioPlayerGL',
                                  homogeneous=True, mode=elm.ELM_LIST_COMPRESS,
                                  select_on_focus=False, focus_on_select=False)
        self._gl.callback_activated_add(self._genlist_item_activated_cb)
        self.content_set('playlist.swallow', self._gl)
        self._gl_populate()

        ### swallow ourself in the main layout and show
        gui.swallow_set('audioplayer.swallow', self)
        self.show()

    def delete(self):
        if self._slider_timer:
            self._slider_timer.delete()
            self._slider_timer = None
        self.signal_callback_add('audioplayer,hide,done', '', self._delete_real)
        self.pause()
        self.hide()

    def _delete_real(self, obj, sig, src):
        EmcPlayerBase.delete(self)
        gui.EmcLayout.delete(self)

    def show(self):
        input_events.listener_add('EmcAudioPlayer', self._input_events_cb)
        events.listener_add('EmcAudioPlayer', self._events_cb)
        self.signal_emit('audioplayer,show', 'emc')
        self.focus_allow = True
        self.tree_focus_allow = False

    def hide(self):
        input_events.listener_del('EmcAudioPlayer')
        events.listener_del('EmcAudioPlayer')
        self.signal_emit('audioplayer,hide', 'emc')
        self.focus_allow = False
        self.tree_focus_allow = False

    def controls_show(self):
        if not self._controls_visible:
            self._controls_visible = True
            input_events.listener_promote('EmcAudioPlayer')
            self.signal_emit('audioplayer,expand', 'emc')
            if self._slider_timer is None:
                self._slider_timer = ecore.Timer(1.0, self._update_timer)
            self._update_timer(single=True)
            self.tree_focus_allow = True

    def controls_hide(self):
        if self._controls_visible:
            self._controls_visible = False
            self.signal_emit('audioplayer,contract', 'emc')
            if self._slider_timer:
                self._slider_timer.delete()
                self._slider_timer = None
            self.tree_focus_allow = False

    def _gl_populate(self):
        self._gl.clear()
        for item in playlist.items:
            it = self._gl.item_append(self._itc, item)
            if item == playlist.onair_item:
                it.selected = True
                it.show()

    def _info_update(self):
        # update metadata infos
        metadata = playlist.onair_item.metadata
        title = elm.utf8_to_markup(metadata.get('title') or _('Unknown title'))
        artist = elm.utf8_to_markup(
            metadata.get('artist') or _('Unknown artist'))
        album = elm.utf8_to_markup(metadata.get('album') or _('Unknown album'))
        self.part_text_set('artist.text', artist)
        self.part_text_set('album.text', album)
        self.part_text_set('song_and_artist.text',
                           '<song>{0}</song> <artist>{1} {2}</artist>'.format(
                               title, _('by'), artist))
        poster = metadata.get('poster')
        img = EmcImage(poster or 'special/cd/' + album)
        self.content_set('cover.swallow', img)

        # update selected playlist item
        it = self._gl.nth_item_get(playlist.cur_idx)
        if it:
            it.selected = True
            it.show()

        # update the slider and the play/pause button
        self._update_timer(single=True)
        self.name_find('PlayPauseBtn').icon_set('icon/pause')

    ## genlist item class
    def _gl_text_get(self, obj, part, pl_item):
        metadata = pl_item.metadata
        if part == 'elm.text.tracknum':
            return str(metadata.get('tracknumber'))
        if part == 'elm.text.title':
            return metadata.get('title') or _('Unknown title')
        if part == 'elm.text.artist':
            return metadata.get('artist') or _('Unknown artist')
        if part == 'elm.text.len':
            seconds = metadata.get('length')
            if seconds is not None:
                return utils.seconds_to_duration(seconds)

    def _genlist_item_activated_cb(self, gl, it):
        playlist_item = it.data
        playlist_item.play()

    def _update_timer(self, single=False):
        self._pos_slider.value = self.position_percent
        self._pos_slider.unit_format = utils.seconds_to_duration(
            self.play_length)
        self._pos_slider.indicator_format = utils.seconds_to_duration(
            self.position)
        return ecore.ECORE_CALLBACK_CANCEL if single else ecore.ECORE_CALLBACK_RENEW

    ### slider callbacks
    def _vol_slider_changed_cb(self, sl):
        volume_set(sl.value * 100)

    def _pos_slider_changed_cb(self, sl):
        self.position_percent = sl.value

    ### buttons callbacks
    def _toggle_loop_cb(self, b):
        playlist.loop = not playlist.loop
        ini.set('mediaplayer', 'playlist_loop', playlist.loop)

    def _toggle_shuffle_cb(self, b):
        playlist.shuffle = not playlist.shuffle
        ini.set('mediaplayer', 'playlist_shuffle', playlist.shuffle)

    ### emotion obj callbacks
    def _playback_started_cb(self, vid):
        events.event_emit('PLAYBACK_STARTED')
        self._info_update()

    def _playback_finished_cb(self, vid):
        events.event_emit('PLAYBACK_FINISHED')
        playlist.play_next()

    ### focus manager
    def _focused_cb(self, obj):
        if self._controls_visible:
            self.controls_hide()
        else:
            self.controls_show()
            self._gl.focus = True

    def focus_move_internal(self, direction):
        if self.focus_move(direction) == False:
            if direction == 'LEFT':  # TODO: this is not themeable !!
                self.controls_hide()
                return True
        return True

    ### input events
    def _input_events_cb(self, event):
        if event == 'OK':
            if self._gl.focus == True:
                self._genlist_item_activated_cb(self._gl, self._gl.focused_item)
                return input_events.EVENT_BLOCK
        elif event == 'BACK':
            if self._controls_visible:
                self.controls_hide()
                self.focus = False
                return input_events.EVENT_BLOCK
        elif event == 'PLAYLIST_NEXT':
            playlist.play_next()
            return input_events.EVENT_BLOCK
        elif event == 'PLAYLIST_PREV':
            playlist.play_prev()
            return input_events.EVENT_BLOCK

        return input_events.EVENT_CONTINUE

    ### generic events
    def _events_cb(self, event):
        if event == 'PLAYBACK_PAUSED':
            self.name_find('PlayPauseBtn').icon_set('icon/play')

        elif event == 'PLAYBACK_UNPAUSED':
            self.name_find('PlayPauseBtn').icon_set('icon/pause')

        elif event == 'PLAYLIST_CHANGED':
            self._gl_populate()

        elif event == 'VOLUME_CHANGED':
            self._vol_slider.step = volume_step_get() / 100.0
            self._vol_slider.value = volume_get() / 100.0

        elif event == 'PLAYBACK_SEEKED':
            # emotion need some loop to update the position, so
            # we need a bit delay to show the updated position.
            ecore.Timer(0.05, lambda: self._update_timer(single=True))
"""

###############################################################################
# emotion_events_map = {
#     'UP': emotion.EMOTION_EVENT_UP,
#     'DOWN': emotion.EMOTION_EVENT_DOWN,
#     'LEFT': emotion.EMOTION_EVENT_LEFT,
#     'RIGHT': emotion.EMOTION_EVENT_RIGHT,
#     'OK': emotion.EMOTION_EVENT_SELECT,
#     'TOGGLE_DVD_MENU': emotion.EMOTION_EVENT_MENU1,
# }

"""
class EmcVideoPlayer(gui.EmcLayout, EmcPlayerBase):
    # This will be overridden by the omx_player
    video_player_cannot_be_covered = False

    def __init__(self, url=None):

        self._play_pause_btn = None
        self._update_timer = None
        self._buffer_dialog = None
        self._controls_visible = False
        self._title = None

        self._minipos_visible = False
        self._minipos_timer = None

        self._subtitles = None  # Subtitle class instance
        self._subs_timer = None  # Timer for subtitles update
        self._subs_notify = None  # EmcNotify for subtitles delay changes

        ### init the layout
        gui.EmcLayout.__init__(self, gui.layout, name='VideoPlayerLayout',
                               file=(gui.theme_file, 'emc/videoplayer/default'),
                               focus_allow=True, is_focus_manager=True)
        self.focus = True

        # left click on video to show/hide the controls
        self.signal_callback_add('mouse,down,1', 'events.rect',
                                 lambda a, s, d: self.controls_toggle())

        # middle click on video to toggle fullscreen
        self.signal_callback_add('mouse,down,2', 'events.rect',
                                 lambda a, s, d: gui.fullscreen_toggle())

        ### init the base player class
        EmcPlayerBase.__init__(self)
        if self.video_object_get():
            self.content_set('video.swallow', self.video_object_get())
        self.url = url

        ### control buttons
        bt = EmcButton(self, icon='icon/fbwd', cb=lambda b: self.fbackward())
        self.box_append('controls.btn_box', bt)

        bt = EmcButton(self, icon='icon/bwd', cb=lambda b: self.backward())
        self.box_append('controls.btn_box', bt)

        bt = EmcButton(self, icon='icon/stop', cb=lambda b: stop(True))
        self.box_append('controls.btn_box', bt)

        bt = EmcButton(self, icon='icon/pause',
                       cb=lambda b: self.pause_toggle())
        self.box_append('controls.btn_box', bt)
        self._play_pause_btn = bt
        bt.name = 'VideoPlayer.PlayBtn'

        bt = EmcButton(self, icon='icon/fwd', cb=lambda b: self.forward())
        self.box_append('controls.btn_box', bt)

        bt = EmcButton(self, icon='icon/ffwd', cb=lambda b: self.fforward())
        self.box_append('controls.btn_box', bt)

        bt = EmcButton(self, _('Audio'), cb=self._audio_menu_build)
        self.box_append('controls.btn_box2', bt)

        bt = EmcButton(self, _('Video'), cb=self._video_menu_build)
        self.box_append('controls.btn_box2', bt)

        bt = EmcButton(self, _('Subtitles'), cb=self._subs_menu_build)
        self.box_append('controls.btn_box2', bt)

        ### position slider
        self._pos_slider = EmcSlider(self, name='VideoPlayer.PosSlider',
                                     indicator_show=False)
        self._pos_slider.callback_changed_add(
            lambda s: setattr(self, 'position_percent', s.value))
        self.content_set('controls.slider', self._pos_slider)

        ### minipos slider
        self._minipos_slider = EmcSlider(self, focus_allow=False)
        self.content_set('minipos.slider', self._minipos_slider)

        ### swallow ourself in the main layout and show
        gui.swallow_set('videoplayer.swallow', self)
        gui.signal_emit('videoplayer,show')

        ### listen to input and generic events
        input_events.listener_add('EmcVideoPlayer', self._input_events_cb)
        events.listener_add('EmcVideoPlayer', self._events_cb)

        ### start the update timer
        self._update_timer = ecore.Timer(1.0, self._update_timer_cb)

        ### try to load subtitles (only for local files)
        if self.url.startswith('file://'):
            self._subtitles = Subtitles(self.url)
            self._subs_timer = ecore.Timer(0.2, self._update_subs_timer_cb)

        ### set title + poster
        if _onair_title: self.title_set(_onair_title)
        if _onair_poster: self.poster_set(_onair_poster)

    def delete(self):
        input_events.listener_del('EmcVideoPlayer')
        events.listener_del('EmcVideoPlayer')
        if self._update_timer:  self._update_timer.delete()
        if self._buffer_dialog: self._buffer_dialog.delete()
        if self._subtitles:     self._subtitles.delete()
        if self._subs_timer:    self._subs_timer.delete()
        if self._subs_notify:   self._subs_notify.delete()

        self.controls_hide()
        gui.signal_emit('videoplayer,hide')
        gui.signal_cb_add('videoplayer,hide,done', '', self._delete_real)

    def _delete_real(self, obj, sig, src):
        gui.signal_cb_del('videoplayer,hide,done', '', self._delete_real)
        EmcPlayerBase.delete(self)
        elm.Layout.delete(self)

    def title_set(self, title):
        self._title = title
        self.part_text_set("controls.title", title)

    def poster_set(self, poster):
        img = EmcImage(poster or 'image/dvd_cover_blank.png')
        img.size_hint_align = (0.5, 0.0)
        self.content_set("controls.poster", img)

    ### controls
    def controls_show(self):
        self.minipos_hide()
        if self.video_player_cannot_be_covered:
            self.signal_emit('controls,show,no_overlap', 'emc')
        else:
            self.signal_emit('controls,show', 'emc')
        self._controls_visible = True

        self._update_slider()
        gui.volume_show(persistent=True)
        if self.focused_object in (None, self):
            self._play_pause_btn.focus = True

    def controls_hide(self):
        if self.video_player_cannot_be_covered:
            self.signal_emit('controls,hide,no_overlap', 'emc')
        else:
            self.signal_emit('controls,hide', 'emc')
        self._controls_visible = False
        gui.volume_hide()

    def controls_toggle(self):
        if self._controls_visible:
            self.controls_hide()
        else:
            self.controls_show()

    ### minipos
    def minipos_show(self):
        if not self._controls_visible:
            if self.video_player_cannot_be_covered:
                self.signal_emit('minipos,show,no_overlap', 'emc')
            else:
                self.signal_emit('minipos,show', 'emc')
            self._minipos_visible = True
            self._update_slider()

            if self._minipos_timer is None:
                self._minipos_timer = ecore.Timer(3, self._minipos_timer_cb)
            else:
                self._minipos_timer.reset()

    def minipos_hide(self):
        if self.video_player_cannot_be_covered:
            self.signal_emit('minipos,hide,no_overlap', 'emc')
        else:
            self.signal_emit('minipos,hide', 'emc')
        self._minipos_visible = False
        if self._minipos_timer:
            self._minipos_timer.delete()
            self._minipos_timer = None

    def _minipos_timer_cb(self):
        self.minipos_hide()
        return ecore.ECORE_CALLBACK_RENEW  # as it is yet deleted in minipos_hide()

    ### subtitles
    def subs_delay_more(self):
        self.subs_delay_apply(+100)

    def subs_delay_less(self):
        self.subs_delay_apply(-100)

    def subs_delay_zero(self):
        self.subs_delay_apply(0)

    def subs_delay_apply(self, diff):
        if self._subtitles is not None:
            if diff == 0:
                self._subtitles.delay = 0
            else:
                self._subtitles.delay += diff
            LOG('Subs delay: %d ms' % self._subtitles.delay)

    def _subtitles_delay_notify(self):
        txt = '<title>%s</><br>%s' % (_('Subtitles'),
                                      _('Delay: %d ms') % self._subtitles.delay)
        if self._subs_notify is None:
            self._subs_notify = EmcNotify(text=txt, icon='icon/subs', hidein=2,
                                          close_cb=self._subtitles_delay_notify_cb)
        else:
            self._subs_notify.text_set(txt)
            self._subs_notify.hidein(2)

    def _subtitles_delay_notify_cb(self):
        self._subs_notify = None

    def _update_subs_timer_cb(self):
        if self._subtitles:
            self._subtitles.update(self.position)
        return ecore.ECORE_CALLBACK_RENEW

    ### internals
    def _update_slider(self):
        pos = self.position_percent
        pos_str = utils.seconds_to_duration(self.position, True)
        len_str = utils.seconds_to_duration(self.play_length, True)

        if self._controls_visible:
            self._pos_slider.value = pos
            self.text_set('controls.position', pos_str)
            self.text_set('controls.length', len_str)
            self.text_set('clock', datetime.now().strftime('%H:%M'))

        if self._minipos_visible:
            self._minipos_slider.value = pos
            self.text_set('minipos.position', pos_str)
            self.text_set('minipos.length', len_str)

    def _update_timer_cb(self):
        if self._buffer_dialog is not None:
            self._buffer_dialog.progress_set(self.buffer_size)
            if self.buffer_size >= 1.0:
                # self._emotion.play = True
                self.unpause()
                self._buffer_dialog.delete()
                self._buffer_dialog = None

        elif self.buffer_size < 1.0:
            self._buffer_dialog = EmcDialog(title=_('Buffering'),
                                            style='buffering')
            # self._emotion.play = False
            self.pause()

        self._update_slider()

        # keep the screensaver out while playing videos
        # if self._emotion.play == True:
        if self.paused == False:
            events.event_emit('KEEP_ALIVE')

        return ecore.ECORE_CALLBACK_RENEW

    ### audio menu
    def _audio_menu_build(self, btn):
        menu = EmcMenu(relto=btn)

        # audio channels
        for trk in self.audio_tracks:
            if trk.name:
                name = _('Audio track: %s') % trk.name
            else:
                name = _('Audio track #%d') % (trk.idx + 1)
            icon = 'icon/item_sel' if trk.active else 'icon/item_nosel'
            menu.item_add(name, icon, None, self._audio_menu_track_cb, trk.idx)

        # mute / unmute
        menu.item_separator_add()
        end_icon = 'icon/check_on' if volume_mute_get() else 'icon/check_off'
        menu.item_add(_('Mute'), 'icon/mute', end_icon,
                      lambda m, i: volume_mute_toggle())

        # and finally show the menu
        menu.show()

    def _audio_menu_track_cb(self, menu, item, track_num):
        self.selected_audio_track = track_num

    ### video menu
    def _video_menu_build(self, btn):
        menu = EmcMenu(relto=btn)

        # video channels
        for trk in self.video_tracks:
            if trk.name:
                name = _('Video track: %s') % trk.name
            else:
                name = _('Video track #%d') % (trk.idx + 1)
            icon = 'icon/item_sel' if trk.active else 'icon/item_nosel'
            item = menu.item_add(name, icon, None, self._video_menu_track_cb,
                                 trk.idx)

        # download
        menu.item_separator_add()
        it = menu.item_add(_('Download video'), 'icon/download',
                           callback=self._video_menu_download_cb)
        if self.url.startswith('file://'):
            it.disabled = True

        # and finally show the menu
        menu.show()

    def _video_menu_track_cb(self, menu, item, track_num):
        self.selected_video_track = track_num

    def _video_menu_download_cb(self, menu, item):
        DownloadManager().queue_download(self.url, self._title)

    ### subtitles menu
    def _subs_menu_build(self, btn):
        menu = EmcMenu(relto=btn)

        # no subs for online videos
        if not self.url.startswith('file://'):
            it = menu.item_add(_('No subtitles'))
            it.disabled = True
            return

        # delay item
        menu.item_add(_('Delay: %d ms') % self._subtitles.delay,
                      callback=self._subs_menu_delay_cb)
        menu.item_separator_add()

        # no subs item
        nos_it = menu.item_add(_('No subtitles'), 'icon/item_nosel',
                               callback=self._subs_menu_track_cb)

        # embedded subs
        spu_cnt = self._emotion.spu_channel_count()
        current = -1 if self._emotion.spu_mute else self._emotion.spu_channel
        for n in range(spu_cnt):
            name = self._emotion.spu_channel_name_get(n) or _(
                'Subtitle #%d') % (n + 1)
            icon = 'icon/item_sel' if n == current else 'icon/item_nosel'
            menu.item_add(name, icon, None, self._subs_menu_track_cb, n)

        # external subs
        for sub in self._subtitles.search_subs():
            if sub.startswith(utils.user_conf_dir):
                name = os.path.basename(sub)[33:]
            else:
                name = os.path.basename(sub)
            icon = 'icon/item_sel' if sub == self._subtitles.current_file else 'icon/item_nosel'
            menu.item_add(name, icon, None, self._subs_menu_track_cb, sub)

        # no subs item
        if current < 0 and self._subtitles.current_file is None:
            menu.item_icon_set(nos_it, 'icon/item_sel')

        # download item
        menu.item_separator_add()
        menu.item_add(_('Download subtitles'), 'icon/subs',
                      callback=self._subs_menu_download_cb)

        # and finally show the menu
        menu.show()

    def _subs_menu_delay_cb(self, menu, item):
        dia = EmcDialog(title=_('Subtitles delay'), style='minimal',
                        text=_('Delay: %d ms') % self._subtitles.delay)
        dia.button_add(_('+100 ms'), self._subs_dia_delay_cb, (dia, +100))
        dia.button_add(_('Reset'), self._subs_dia_delay_cb, (dia, 0))
        dia.button_add(_('-100 ms'), self._subs_dia_delay_cb, (dia, -100))

    def _subs_dia_delay_cb(self, btn, data):
        dia, offset = data
        self.subs_delay_apply(offset)
        dia.text_set(_('Delay: %d ms') % self._subtitles.delay)

    def _subs_menu_track_cb(self, menu, item, sub=None):
        if sub is None:  # disable all subs
            self._subtitles.file_set(None)
            self._emotion.spu_mute = True
            self._emotion.spu_channel = -1
        elif isinstance(sub, int):  # embedded sub (track count)
            self._emotion.spu_channel = sub
            self._emotion.spu_mute = False
        else:  # external file
            self._subtitles.file_set(sub)

    def _subs_menu_download_cb(self, menu, item):
        Opensubtitles(self.url, self._subs_download_done)

    def _subs_download_done(self, dest_file):
        self._subtitles.file_set(dest_file)

    ### emotion obj callbacks
    def _playback_started_cb(self, vid):
        events.event_emit('PLAYBACK_STARTED')

    def _playback_finished_cb(self, vid):
        stop(True)

    ### input events
    def _input_events_cb(self, event):

        # DVD menu navigation (send events to emotion)
        # TODO: the play_length check is just a temorary hack (dvd menu are quite
        #       always short videos). We should be able to query number of buttons
        #       in spu, and check num_buttons > 0. But emotion do not (yet)
        #       provide this info, thus the len hack.
        if self._url.startswith('dvd://') and self.play_length < 60:
            if event in emotion_events_map:
                DBG('Sending event: "%s" to emotion for DVD navigation' % event)
                self._emotion.event_simple_send(emotion_events_map[event])
                return input_events.EVENT_BLOCK

        if event == 'TOGGLE_DVD_MENU':
            self._emotion.event_simple_send(emotion_events_map[event])
            return input_events.EVENT_BLOCK

        elif event == 'SUBS_DELAY_MORE':
            if self._subtitles:
                self.subs_delay_more()
                self._subtitles_delay_notify()
            return input_events.EVENT_BLOCK

        elif event == 'SUBS_DELAY_LESS':
            if self._subtitles:
                self.subs_delay_less()
                self._subtitles_delay_notify()
            return input_events.EVENT_BLOCK

        elif event == 'SUBS_DELAY_ZERO':
            if self._subtitles:
                self.subs_delay_zero()
                self._subtitles_delay_notify()
            return input_events.EVENT_BLOCK

        elif event == 'EXIT':
            stop(True)
            return input_events.EVENT_BLOCK

        if self._controls_visible:
            if event == 'OK':
                pass
            elif event == 'BACK':
                self.controls_hide()
                return input_events.EVENT_BLOCK

        else:
            if event == 'OK':
                self.controls_show()
                return input_events.EVENT_BLOCK
            elif event == 'BACK':
                stop(True)
                return input_events.EVENT_BLOCK
            elif event == 'RIGHT':
                self.forward()
                return input_events.EVENT_BLOCK
            elif event == 'LEFT':
                self.backward()
                return input_events.EVENT_BLOCK
            elif event == 'UP':
                input_events.event_emit('VOLUME_UP')
                return input_events.EVENT_BLOCK
            elif event == 'DOWN':
                input_events.event_emit('VOLUME_DOWN')
                return input_events.EVENT_BLOCK

        return input_events.EVENT_CONTINUE

    ### generic events
    def _events_cb(self, event):
        if event == 'PLAYBACK_PAUSED':
            self._play_pause_btn.icon_set('icon/play')
            self.signal_emit('minipos,pause,set', 'emc')
        elif event == 'PLAYBACK_UNPAUSED':
            self._play_pause_btn.icon_set('icon/pause')
            self.signal_emit('minipos,play,set', 'emc')
        elif event == 'PLAYBACK_SEEKED':
            # emotion need some loop to update the position, so
            # we need a bit delay to show the updated position.
            ecore.Timer(0.05, lambda: self._update_slider())

        # show minipos on seek/pause/play
        if not self._controls_visible and self.position > 1:
            if event in (
            'PLAYBACK_PAUSED', 'PLAYBACK_UNPAUSED', 'PLAYBACK_SEEKED'):
                ecore.Timer(0.05, lambda: self.minipos_show())
"""

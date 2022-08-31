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
from typing import Callable, List

from PySide6 import QtCore, QtMultimedia

from nepymc.gui import EmcGui, EmcVideoPlayer
from nepymc import mediaplayer
from nepymc.mediaplayer import MediaTrack


def LOG(*args):
    print('VP_QT:', *args)


def ERR(*args):
    print('VP_QT ERROR:', *args, file=sys.stderr)


def DBG(*args):
    print('VP_QT:', *args)
    pass


class MenuItem(object):
    def __init__(self, label: str = None, icon: str = None,
                 checkable: bool = False, checked: bool = False,
                 disabled: bool = False, is_separator: bool = False,
                 callback: Callable = None, **kargs):
        self.label = label
        self.icon = icon
        self.checkable = checkable
        self.checked = checked
        self.disabled = disabled
        self.is_separator = is_separator
        self.callback = callback
        self.callback_kargs = kargs

    def activate(self):
        if callable(self.callback):
            self.callback(self, **self.callback_kargs)


class MenuModelBase(QtCore.QAbstractListModel):
    label_role = QtCore.Qt.UserRole + 1
    icon_role = QtCore.Qt.UserRole + 2
    is_separator = QtCore.Qt.UserRole + 4
    checkable = QtCore.Qt.UserRole + 5
    checked = QtCore.Qt.UserRole + 6
    disabled = QtCore.Qt.UserRole + 7

    role_names = {
        label_role: b'label',
        icon_role: b'icon',
        is_separator: b'is_separator',
        checkable: b'checkable',
        checked: b'checked',
        disabled: b'disabled',
    }

    def __init__(self):
        super().__init__()
        self.items: List[MenuItem] = []

    def roleNames(self):
        return self.role_names

    def rowCount(self, index):
        return len(self.items)

    def data(self, index, role):
        item = self.items[index.row()]  # type: MenuItem
        if role == self.label_role:
            return item.label or ''
        elif role == self.icon_role:
            return item.icon or ''
        elif role == self.is_separator:
            return item.is_separator
        elif role == self.checkable:
            return item.checkable
        elif role == self.checked:
            return item.checked
        elif role == self.disabled:
            return item.disabled

    # below methods are to be called from QML
    @QtCore.Slot()
    def populate(self):
        """ Called from QML just before showing the menu """
        self.beginResetModel()
        self.endResetModel()

    @QtCore.Slot(int)
    def item_activated(self, index):
        item = self.items[index]
        item.activate()


class AudioMenuModel(MenuModelBase):
    def populate(self):
        self.beginResetModel()
        self.items = []
        for t in mediaplayer.audio_tracks_get():
            self.items.append(MenuItem('%s - %s' % (t.name, t.lang),
                                       checkable=True, checked=t.active,
                                       callback=self.change_track, track=t))
        self.items.append(MenuItem(is_separator=True))
        self.items.append(MenuItem(_('Mute'), 'icon/mute', checkable=True,
                                   checked=mediaplayer.volume_mute_get(),
                                   callback=self.mute_toggle))
        self.endResetModel()

    @staticmethod
    def mute_toggle(_item):
        mediaplayer.volume_mute_toggle()

    @staticmethod
    def change_track(_item, track):
        mediaplayer.audio_track_set(track.idx)


class VideoMenuModel(MenuModelBase):
    def populate(self):
        self.beginResetModel()
        self.items = []
        for t in mediaplayer.video_tracks_get():
            self.items.append(MenuItem(t.name,
                                       checkable=True, checked=t.active,
                                       callback=self.change_track, track=t))
        self.items.append(MenuItem(is_separator=True))
        self.items.append(MenuItem(_('Download video'), icon='icon/download'))
        self.endResetModel()

    @staticmethod
    def change_track(_item, track):
        mediaplayer.audio_track_set(track.idx)


class SubsMenuModel(MenuModelBase):
    def populate(self):
        self.beginResetModel()
        tracks = mediaplayer.subtitle_tracks_get()
        self.items = [
            MenuItem(_('No subtitles'), checkable=True,
                     checked=mediaplayer.subtitle_track_get() == -1,
                     callback=self.disable_subs),
        ]
        if len(tracks) > 0:
            self.items.append(MenuItem(is_separator=True))
        for t in tracks:
            self.items.append(MenuItem('%s - %s' % (t.name, t.lang),
                                       checkable=True, checked=t.active,
                                       callback=self.change_track, track=t))
        self.endResetModel()

    @staticmethod
    def change_track(_item, track):
        mediaplayer.subtitle_track_set(track.idx)

    @staticmethod
    def disable_subs(_item):
        mediaplayer.subtitle_track_set(-1)


class EmcVideoPlayer_Qt(EmcVideoPlayer):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        print("INIT VIDEO PLAYER QT")

        self._gui = EmcGui.instance()

        self._audio_menu_model = AudioMenuModel()
        self._video_menu_model = VideoMenuModel()
        self._subs_menu_model = SubsMenuModel()

        self._gui.model_set('AudioMenuModel', self._audio_menu_model)
        self._gui.model_set('VideoMenuModel', self._video_menu_model)
        self._gui.model_set('SubsMenuModel', self._subs_menu_model)

        self._qml_obj = self._gui._qml_root.activate_section('videoplayer')

    def delete(self) -> None:
        super().delete()
        # self._qml_obj.emcDestroy()  # TODO call close() in qml??

    @property
    def url(self) -> str:
        return self._qml_obj.property('url')

    @url.setter
    def url(self, url: str) -> None:
        self._qml_obj.setProperty('url', url)

    @property
    def position(self) -> int:
        """ millis """
        return self._qml_obj.property('position')

    @position.setter
    def position(self, val: int):
        self._qml_obj.seek(val)

    @property
    def duration(self) -> int:
        """ millis """
        return self._qml_obj.property('duration')

    def volume_set(self, val: float) -> None:
        self._qml_obj.setProperty('volume', val / 100.0)

    def volume_mute_set(self, muted: bool) -> None:
        self._qml_obj.setProperty('muted', muted)

    def play(self) -> None:
        # make sure the videplayer is visible and focused
        self._gui.activate_section('videoplayer')
        self._qml_obj.play()

    def pause(self) -> None:
        self._qml_obj.pause()

    def stop(self) -> None:
        self._qml_obj.stop()

    def title_set(self, title: str) -> None:
        self._qml_obj.setProperty('title', title)

    def poster_set(self, poster: str) -> None:
        self._qml_obj.setProperty('poster', poster)

    @property
    def audio_tracks(self) -> List[MediaTrack]:
        li = []
        tracks = self._qml_obj.property('audioTracks')
        for i, t in enumerate(tracks):
            title = t.stringValue(QtMultimedia.QMediaMetaData.Key.Title)
            mt = MediaTrack(
                i,
                t.stringValue(QtMultimedia.QMediaMetaData.Key.Language),
                title or _('Track %d') % (i + 1),
                t.stringValue(QtMultimedia.QMediaMetaData.Key.AudioCodec),
                i == self.selected_audio_track
            )
            li.append(mt)
        return li

    @property
    def selected_audio_track(self) -> int:
        return self._qml_obj.property('audioTrack')

    @selected_audio_track.setter
    def selected_audio_track(self, idx: int) -> None:
        self._qml_obj.setProperty('audioTrack', idx)

    @property
    def video_tracks(self) -> List[MediaTrack]:
        li = []
        tracks = self._qml_obj.property('videoTracks')
        for i, t in enumerate(tracks):
            title = t.stringValue(QtMultimedia.QMediaMetaData.Key.Title)
            mt = MediaTrack(
                i,
                t.stringValue(QtMultimedia.QMediaMetaData.Key.Language),
                title or _('Track %d') % (i + 1),
                t.stringValue(QtMultimedia.QMediaMetaData.Key.VideoCodec),
                i == self.selected_video_track
            )
            li.append(mt)
        return li

    @property
    def selected_video_track(self) -> int:
        return self._qml_obj.property('videoTrack')

    @selected_video_track.setter
    def selected_video_track(self, idx: int) -> None:
        self._qml_obj.setProperty('videoTrack', idx)

    @property
    def subtitle_tracks(self) -> List[MediaTrack]:
        li = []
        tracks = self._qml_obj.property('subtitleTracks')
        for i, t in enumerate(tracks):
            title = t.stringValue(QtMultimedia.QMediaMetaData.Key.Title)
            mt = MediaTrack(
                i,
                t.stringValue(QtMultimedia.QMediaMetaData.Key.Language),
                title or _('Track %d') % (i + 1),
                None,  # codec?
                i == self.selected_subtitle_track
            )
            li.append(mt)
        return li

    @property
    def selected_subtitle_track(self) -> int:
        return self._qml_obj.property('subtitleTrack')

    @selected_subtitle_track.setter
    def selected_subtitle_track(self, idx: int) -> None:
        self._qml_obj.setProperty('subtitleTrack', idx)

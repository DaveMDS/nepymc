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
from operator import itemgetter
from urllib.parse import urlencode

import nepymc.utils as utils
from nepymc.gui import EmcDialog
from nepymc.mainloop import EmcUrl


def DBG(*args):
    print('TMDB:', *args)
    pass


TMDB_API_KEY = '19eef197b81231dff0fd1a14a8d5f863'  # Key of the user DaveMDS
DEFAULT_INFO_LANG = 'en'


def get_poster_filename(movie_id):
    return os.path.join(utils.user_conf_dir, 'movies',
                        str(movie_id), 'poster.jpg')


def get_icon_filename(movie_id):
    return os.path.join(utils.user_conf_dir, 'movies',
                        str(movie_id), 'icon.jpg')


def get_backdrop_filename(movie_id):
    return os.path.join(utils.user_conf_dir, 'movies',
                        str(movie_id), 'backdrop.jpg')


def get_tv_backdrop_filename(tvshows_id):
    return os.path.join(utils.user_conf_dir, 'tvshows',
                        str(tvshows_id), 'backdrop.jpg')


def get_tv_poster_filename(tvshows_id, season_num=None, episode_id=None):
    if episode_id is not None:
        return os.path.join(utils.user_conf_dir, 'tvshows',
                            str(tvshows_id), '%s.jpg' % episode_id)
    elif season_num is not None:
        return os.path.join(utils.user_conf_dir, 'tvshows',
                            str(tvshows_id), 'poster_s%d.jpg' % season_num)
    else:
        return os.path.join(utils.user_conf_dir, 'tvshows',
                            str(tvshows_id), 'poster.jpg')


def get_tv_icon_filename(tvshows_id, season_num=None):
    if season_num is not None:
        return os.path.join(utils.user_conf_dir, 'tvshows',
                            str(tvshows_id), 'icon_s%d.jpg' % season_num)
    else:
        return os.path.join(utils.user_conf_dir, 'tvshows',
                            str(tvshows_id), 'icon.jpg')


class TMDBv3(object):
    """ TMDB API v3

    tmdb = TMDBv3()

    # search for a given movie name + year:
    tmdb.movie_search('Alien', 1979, search_done_cb)
    def search_done_cb(tmdb_obj, results):

    # get movie info + poster + backdrop:
    tmdb.get_movie_info(tmdb_id, info_done_cb, info_progress_cb)
    def info_progress_cb(tmdb, progress):
    def info_done_cb(tmdb, movie_info):

    # get list of all available posters:
    tmdb.get_posters(tmdb_id, list_complete_cb)
    def list_complete_cb(tmdb, posters):

    # get list of all available backdrop:
    tmdb.get_backdrops(tmdb_id, list_complete_cb)
    def list_complete_cb(tmdb, backdrops):

    # get info for a list of casts
    tmdb.get_cast_info(cast_ids, cast_done_cb):
    def cast_done_cb(tmdb, result):

    # abort the current operation:
    tmdb.abort()

    """
    def __init__(self, api_key=TMDB_API_KEY, lang=DEFAULT_INFO_LANG):
        self.key = api_key
        self.lang = lang
        self.base_url = 'http://api.themoviedb.org/3'
        self.base_url_img = 'http://image.tmdb.org/t/p'  # from /3/configuration
        self.api_handler = None
        self.dwl_handler = None
        self.done_cb = None
        self.progress_cb = None
        self.download_total = 0
        self.dqueue_images = None
        self.dqueue_seasons = None
        self.dqueue_seasons_fb = None
        self.dqueue_total = 0

    # abort the current operation
    def abort(self):
        if self.dwl_handler:
            self.dwl_handler.delete()
            self.dwl_handler = None
        if self.api_handler:
            self.api_handler.delete()
            self.api_handler = None

    # --- api helpers  ---------------------------------------------------------
    def _api_url(self, entry_point, **kargs):
        if 'api_key' not in kargs:
            kargs['api_key'] = self.key
        if 'language' not in kargs:
            kargs['language'] = self.lang
        return self.base_url + entry_point + '?' + urlencode(kargs)

    def _api_call(self, callback, cb_data, entry_point, **kargs):
        url = self._api_url(entry_point, **kargs)
        DBG('TMDB API CALL: ' + url)
        self.api_handler = EmcUrl(url, dest='::mem::', decode='json',
                                  urlencode=False,
                                  done_cb=self._api_call_done_cb,
                                  user_callback=callback,
                                  user_data=cb_data)

    def _api_call_done_cb(self, url, success, data, user_callback, user_data):
        self.api_handler = None
        if user_data:
            user_callback(data, user_data)
        else:
            user_callback(data)

    def _img_url(self, final_part, size):
        if final_part:
            return self.base_url_img + '/' + size + final_part

    # --- movie search ---------------------------------------------------------
    def movie_search(self, name, year, done_cb):
        if year:
            self._api_call(self._movie_search_done, done_cb,
                           '/search/movie', query=name, year=year)
        else:
            self._api_call(self._movie_search_done, done_cb,
                           '/search/movie', query=name)

    def _movie_search_done(self, api_data, done_cb):
        results = []
        for result in api_data['results']:
            try:
                results.append({
                    'tmdb_id': result['id'],
                    'title': result['title'],
                    'year': result['release_date'][:4],
                    'poster_url': self._img_url(result['poster_path'], 'w154')
                })
            except KeyError:
                pass
        done_cb(self, results)

    # --- get movie info -------------------------------------------------------
    def get_movie_info(self, tid, done_cb, progress_cb=None):
        self.done_cb = done_cb
        self.progress_cb = progress_cb

        self._api_call(self._movie_info_done, None,
                       '/movie/%s' % tid, append_to_response='credits')

    def _movie_info_done(self, api_data):
        # create the movie info dict
        try:
            director = [d['name'] for d in api_data['credits']['crew']
                        if d['job'] == 'Director'][0]
        except KeyError:
            director = 'missing'

        try:
            country = api_data['production_countries'][0]['iso_3166_1']
        except KeyError:
            country = ''

        try:
            countries = ', '.join(
                [c['iso_3166_1'] for c in api_data['production_countries']])
        except KeyError:
            countries = ''

        for cast in api_data['credits']['cast']:
            cast['profile_path'] = self._img_url(cast['profile_path'], 'w154')

        for cast in api_data['credits']['crew']:
            cast['profile_path'] = self._img_url(cast['profile_path'], 'w154')

        self.movie_info = {
            'id': api_data['id'],
            'tmdb_id': api_data['id'],
            'imdb_id': api_data['imdb_id'],
            'title': api_data['title'],
            'adult': api_data['adult'],
            'original_title': api_data['original_title'],
            'release_date': api_data['release_date'],
            'budget': api_data['budget'],
            'overview': api_data['overview'],
            'tagline': api_data['tagline'],
            'rating': api_data['vote_average'],
            'country': country,
            'countries': countries,
            'director': director,
            'cast': api_data['credits']['cast'],
            'crew': api_data['credits']['crew'],
        }

        # queue backdrop, poster and icon
        self.dqueue_images = []

        if api_data['backdrop_path'] is not None:
            self.dqueue_images.append(
                (self._img_url(api_data['backdrop_path'], 'w1280'),
                 get_backdrop_filename(api_data['id'])))
        if api_data['poster_path'] is not None:
            self.dqueue_images.append(
                (self._img_url(api_data['poster_path'], 'w500'),
                 get_poster_filename(api_data['id'])))
            self.dqueue_images.append(
                (self._img_url(api_data['poster_path'], 'w92'),
                 get_icon_filename(api_data['id'])))

        # start the multi download loop
        self.download_total = len(self.dqueue_images) + 1
        self._movie_multi_img_download(None, None, None)

    def _movie_multi_img_download(self, url, status, dest):
        self.dwl_handler = None

        # call the progress callback
        if callable(self.progress_cb):
            prog = 1 - (float(len(self.dqueue_images)) / self.download_total)
            self.progress_cb(self, prog)

        # download the next image or end the loop
        if len(self.dqueue_images) > 0:
            url, dest = self.dqueue_images.pop(0)
            DBG("getting img: " + url)
            self.dwl_handler = EmcUrl(url, dest, urlencode=False,
                                      done_cb=self._movie_multi_img_download)
        else:
            self._movie_info_all_done()

    def _movie_info_all_done(self):
        if callable(self.progress_cb):
            self.progress_cb(self, 1.0)
        self.done_cb(self, self.movie_info)

    # --- tv search ------------------------------------------------------------
    def tv_search(self, name, done_cb):
        self._api_call(self._tv_search_done, done_cb,
                       '/search/tv', query=name)

    def _tv_search_done(self, api_data, done_cb):
        results = []
        for result in api_data['results']:
            try:
                air_date = result['first_air_date']
                results.append({
                    'tmdb_id': result['id'],
                    'name': result['name'],
                    'year': air_date[:4] if air_date else None,
                    'poster_url': self._img_url(result['poster_path'], 'w154')
                })
            except KeyError:
                pass
        done_cb(self, results)

    # --- get tv info  ---------------------------------------------------------
    def get_tv_info(self, tid, done_cb, progress_cb=None):
        self.done_cb = done_cb
        self.progress_cb = progress_cb
        self.dqueue_images = []
        self.dqueue_seasons = []
        self.dqueue_seasons_fb = []
        self.dqueue_total = 0
        self._api_call(self._tv_info_done, tid,
                       '/tv/%s' % tid, append_to_response='credits')

    def _tv_info_progress_report(self):
        if callable(self.progress_cb):
            if self.dqueue_total > 0:
                remaining = len(self.dqueue_images) + len(self.dqueue_seasons)
                prog = 1.0 - (remaining / float(self.dqueue_total))
                self.progress_cb(self, prog)
            else:
                self.progress_cb(self, 0.0)

    def _tv_info_done(self, data, tid=None):
        self._tv_info_progress_report()

        # fallback to english if needed
        if not data['overview'] and self.lang != 'en' and tid is not None:
            self._api_call(self._tv_info_done, None, '/tv/%s' % tid,
                           language='en', append_to_response='credits')
            return

        for person in data['credits']['cast']:
            person['profile_path'] = self._img_url(person['profile_path'],
                                                   'w154')

        for person in data['credits']['crew']:
            person['profile_path'] = self._img_url(person['profile_path'],
                                                   'w154')

        # build main tvshow info dict
        self.tv_info = {
            'id': data['id'],
            'name': data['original_name'],
            'overview': data['overview'],
            'created_by': ', '.join([c['name'] for c in data['created_by']]),
            'episode_run_time': ', '.join(map(str, data['episode_run_time'])),
            'first_air_date': data['first_air_date'],
            'last_air_date': data['last_air_date'],
            'genres': ', '.join([g['name'] for g in data['genres']]),
            'networks': ', '.join([n['name'] for n in data['networks']]),
            'number_of_episodes': data['number_of_episodes'],
            'number_of_seasons': data['number_of_seasons'],
            'country': data['origin_country'],
            'status': data['status'],
            'vote_average': data['vote_average'],
            'vote_count': data['vote_count'],
            'cast': data['credits']['cast'],
            'crew': data['credits']['crew'],
            'seasons': {}
        }

        # queue backdrop, poster and icon
        if data['backdrop_path']:
            self.dqueue_images.append(
                (self._img_url(data['backdrop_path'], 'w1280'),
                 get_tv_backdrop_filename(data['id'])))

        if data['poster_path']:
            self.dqueue_images.append(
                (self._img_url(data['poster_path'], 'w500'),
                 get_tv_poster_filename(data['id'])))
            self.dqueue_images.append(
                (self._img_url(data['poster_path'], 'w92'),
                 get_tv_icon_filename(data['id'])))

        for s in data['seasons']:
            # queue posters and icons for each season
            if s['poster_path']:
                self.dqueue_images.append(
                    (self._img_url(s['poster_path'], 'w92'),
                     get_tv_icon_filename(data['id'], s['season_number'])))

                self.dqueue_images.append(
                    (self._img_url(s['poster_path'], 'w500'),
                     get_tv_poster_filename(data['id'], s['season_number'])))

            # queue the season to retrive data
            self.dqueue_seasons.append(s['season_number'])

        # start the download of all the images and all the seasons info
        self.dqueue_total = len(self.dqueue_images) + len(self.dqueue_seasons)
        self._tv_multi_img_download(None, None, None)
        self._tv_multi_season_api(None)

    def _tv_multi_season_api(self, data):
        self._tv_info_progress_report()

        if (data is not None) and (len(data['episodes']) > 0):
            missing_translation = False

            # store the info for this season
            season = {
                'id': data['id'],
                'season_num': data['season_number'],
                'first_air_date': data['air_date'],
                'overview': data['overview'],
                'episodes': {},
            }

            if not data['overview'] and self.lang != 'en':
                missing_translation = True

            # store info for each episode
            for e in data['episodes']:
                season['episodes'][e['episode_number']] = {
                    'id': e['id'],
                    'series_id': self.tv_info['id'],
                    'title': e['name'],
                    'overview': e['overview'],
                    'first_aired': e['air_date'],
                    'episode_num': e['episode_number'],
                    'season_num': season['season_num'],
                    'director': ['TODO'],  # TODO
                    'writer': ['TODO'],  # TODO
                    'thumb_url': self._img_url(e['still_path'], 'w300')
                }

                if (not e['overview'] or not e['name']) and self.lang != 'en':
                    missing_translation = True

            self.tv_info['seasons'][data['season_number']] = season

            if missing_translation:
                self.dqueue_seasons_fb.append(data['season_number'])

        # get the next season if available or end the loop
        if len(self.dqueue_seasons) > 0:
            season = self.dqueue_seasons.pop(0)
            self._api_call(self._tv_multi_season_api, None,
                           '/tv/%d/season/%d' % (self.tv_info['id'], season))
        else:
            self._tv_multi_season_fallback_api(None)

    def _tv_multi_season_fallback_api(self, data):
        self._tv_info_progress_report()
        if (data is not None) and (len(data['episodes']) > 0):
            season = self.tv_info['seasons'][data['season_number']]

            if not season['overview']:
                season['overview'] = data['overview']

            for e in data['episodes']:
                ep = season['episodes'][e['episode_number']]
                if not ep['title']:
                    ep['title'] = e['name']
                if not ep['overview']:
                    ep['overview'] = e['overview']

        # get the next fallback season if available or end the loop
        if len(self.dqueue_seasons_fb) > 0:
            season = self.dqueue_seasons_fb.pop(0)
            self._api_call(self._tv_multi_season_fallback_api, None,
                           '/tv/%d/season/%d' % (self.tv_info['id'], season),
                           language='en')
        else:
            self._tv_info_all_done()

    def _tv_multi_img_download(self, url, status, dest):
        self._tv_info_progress_report()
        self.dwl_handler = None
        if len(self.dqueue_images) > 0:
            url, dest = self.dqueue_images.pop(0)
            DBG("getting img: " + url)
            self.dwl_handler = EmcUrl(url, dest, urlencode=False,
                                      done_cb=self._tv_multi_img_download)
        else:
            self._tv_info_all_done()

    def _tv_info_all_done(self):
        if (len(self.dqueue_images) + len(self.dqueue_seasons) +
                len(self.dqueue_seasons_fb)) > 0:
            return

        self._tv_info_progress_report()
        self.done_cb(self, self.tv_info)

    # --- posters list ---------------------------------------------------------
    def get_posters(self, tmdb_id, done_cb, tv=False):
        langs = '%s,en,null' % self.lang
        entry_point = 'tv' if tv else 'movie'
        self._api_call(self._poster_list_done, done_cb,
                       '/%s/%s/images' % (entry_point, tmdb_id),
                       include_image_language=langs)

    def _poster_list_done(self, api_data, done_cb):
        results = []
        for poster in api_data['posters']:
            results.append({
                'movie_id': api_data['id'],
                'icon_url': self._img_url(poster['file_path'], 'w92'),
                'thumb_url': self._img_url(poster['file_path'], 'w342'),
                'url': self._img_url(poster['file_path'], 'w500'),
                'lsort': 1 if poster['iso_639_1'] == self.lang else 2
            })
        results.sort(key=itemgetter('lsort'))
        done_cb(self, results)

    # --- backdrops list -------------------------------------------------------
    def get_backdrops(self, tmdb_id, done_cb, tv=False):
        langs = '%s,en,null' % self.lang
        entry_point = 'tv' if tv else 'movie'
        self._api_call(self._backdrops_list_done, done_cb,
                       '/%s/%s/images' % (entry_point, tmdb_id),
                       include_image_language=langs)

    def _backdrops_list_done(self, api_data, done_cb):
        results = []
        for backdrop in api_data['backdrops']:
            results.append({
                'movie_id': api_data['id'],
                'thumb_url': self._img_url(backdrop['file_path'], 'w300'),
                'url': self._img_url(backdrop['file_path'], 'w1280'),
                'lsort': 1 if backdrop['iso_639_1'] == self.lang else 2
            })
        results.sort(key=itemgetter('lsort'))
        done_cb(self, results)

    # --- get cast info --------------------------------------------------------
    def person_search(self, name, done_cb):
        self._api_call(self._person_search_done, done_cb,
                       '/search/person', query=name)

    def _person_search_done(self, api_data, done_cb):
        # TODO adjust image urls
        done_cb(self, api_data)

    def get_cast_info(self, cast_id, done_cb):
        self._api_call(self._cast_info_done, done_cb,
                       '/person/%s' % cast_id,
                       append_to_response='credits,images')

    def _cast_info_done(self, api_data, done_cb):
        # adjust image urls
        api_data['profile_path'] = self._img_url(api_data['profile_path'],
                                                 'h632')
        for img in api_data['images']['profiles']:
            img['file_path'] = self._img_url(img['file_path'], 'h632')
        for movie in api_data['credits']['cast']:
            movie['poster_path'] = self._img_url(movie['poster_path'], 'w154')
        for movie in api_data['credits']['crew']:
            movie['poster_path'] = self._img_url(movie['poster_path'], 'w154')

        done_cb(self, api_data)


class CastPanel(object):
    def __init__(self, pid=None, name=None, lang=DEFAULT_INFO_LANG):
        self.pid = pid
        self.info = None

        tmdb = TMDBv3(lang=lang)
        if name:
            tmdb.person_search(name, self._search_done_cb)
        elif pid:
            tmdb.get_cast_info(self.pid, self._fetch_done_cb)
        self._dia = EmcDialog(style='minimal', title=_('Fetching info'),
                              content='image/tmdb_logo.png',
                              spinner=True)

    def _search_done_cb(self, tmdb, result):
        # TODO manage errors
        self.pid = result['results'][0]['id']
        tmdb.get_cast_info(self.pid, self._fetch_done_cb)

    def _fetch_done_cb(self, tmdb, result):
        self.info = result
        self._dia.delete()

        text = ''
        if self.info.get('biography'):
            text += '%s<br><br>' % self.info['biography'].replace('\n', '<br>')
        if self.info.get('birthday'):
            text += '<name>%s:</name> %s<br>' % (
                    _('Birthday'), self.info['birthday'])
        if self.info.get('deathday'):
            text += '<name>%s:</name> %s<br>' % (
                    _('Deathday'), self.info['deathday'])
        if self.info.get('place_of_birth'):
            text += '<name>%s:</name> %s<br>' % (
                    _('Place of birth'), self.info['place_of_birth'])

        self._dia = EmcDialog(title=self.info['name'], style='panel',
                              content=self.info['profile_path'], text=text)

        # merge cast and crew in a single movies list
        movies = {}  # key: tmdbid val: tmdb-data-dict + 'jobs'
        for movie in self.info['credits']['crew']:
            tid = movie['id']
            if tid in movies:
                movies[tid]['jobs'].append(movie.get('job'))
            else:
                movie['jobs'] = [movie.get('job')]
                movies[tid] = movie

        for movie in self.info['credits']['cast']:
            tid = movie['id']
            if tid in movies:
                movies[tid]['character'] = movie.get('character')
            else:
                movies[tid] = movie

        self._dia.button_add(_('Movies (%s)') % len(movies),
                             lambda b: self.movies_dialog(movies))
        num = len(self.info['images']['profiles'])
        self._dia.button_add(_('Photos (%s)') % num,
                             lambda b: self.photos_dialog())

    def photos_dialog(self):
        dia = EmcDialog(style='image_list_portrait', title=self.info['name'])
        for image in self.info['images']['profiles']:
            dia.list_item_append(None, image['file_path'])
        dia.list_go()

    def movies_dialog(self, movies):
        dia = EmcDialog(style='list', title=self.info['name'])
        for movie in sorted(movies.values(), key=itemgetter('title')):
            label = '<big>{}</big>'.format(movie['title'])
            if 'character' in movie:
                label += ' <i>{} <big>{}</big></i>'.format(_('as'),
                                                           movie['character'])
            if 'jobs' in movie:
                label += ' <i>({})</i>'.format(', '.join(movie['jobs']))
            dia.list_item_append(label, movie.get('poster_path'))
        dia.list_go()

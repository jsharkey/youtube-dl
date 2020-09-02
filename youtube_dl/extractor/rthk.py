# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor

import re


class RTHKBaseIE(InfoExtractor):
    def parse_date(self, raw):
        if raw:
            day, month, year = raw.split('/')
            return "%s%s%s" % (year, month, day)
        else:
            return None

    def parse_episode(self, channel_id, programme_id, episode_id):
        video_id = "%s-%s-%s" % (channel_id, programme_id, episode_id)
        url = 'https://www.rthk.hk/tv/%s/programme/%s/episode/%s' % (channel_id, programme_id, episode_id)

        webpage = self._download_webpage(url, video_id)
        m3u8_url = self._search_regex(r'"(https?://.+?/master.m3u8)"', webpage, 'm3u8_url', fatal=True)
        formats = self._extract_m3u8_formats(m3u8_url, video_id, 'mp4', m3u8_id='hls', fatal=False)

        return {
            'id': video_id,
            'formats': formats,
            'title': self._html_search_meta('og:title', webpage, 'title'),
            'thumbnail': self._html_search_meta('og:image', webpage, 'thumbnail'),
            'series': self._html_search_meta('programmeName', webpage, 'series'),
            'episode': self._html_search_meta('episodeName', webpage, 'episode'),
            'release_date': self.parse_date(self._html_search_meta('episodeDate', webpage, 'release_date')),
        }


class RTHKIE(RTHKBaseIE):
    _VALID_URL = r'^https?://(?:www\.)?rthk.hk/tv/(.+?)/programme/(.+?)/episode/(.+?)$'
    _TEST = {
        'url': 'https://www.rthk.hk/tv/dtt31/programme/livingwithanimals/episode/686344',
        'info_dict': {
            'id': 'dtt31-livingwithanimals-686344',
            'ext': 'mp4',
            'title': '港台電視 31 動物愛傳承 - 與牛同行',
            'thumbnail': 'https://www.rthk.hk/tv_thumbnails/tv_livingwithanimals/PETSCT2020M00700003_upload.jpg',
            'series': '動物愛傳承',
            'episode': '與牛同行',
            'release_date': '20200816',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        channel_id, programme_id, episode_id = re.match(self._VALID_URL, url).groups()
        return self.parse_episode(channel_id, programme_id, episode_id)


class RTHKPlaylistIE(RTHKBaseIE):
    _VALID_URL = r'^https?://(?:www\.)?rthk.hk/tv/(.+?)/programme/(.+?)/?$'
    _TEST = {
        'url': 'https://www.rthk.hk/tv/dtt31/programme/hongkongecologists/',
        'info_dict': {
            'id': 'dtt31-hongkongecologists',
        },
        'playlist_mincount': 11,
    }

    PLAYLIST_URL_TEMPLATE = 'https://www.rthk.hk/tv/catchUp?c=%s&p=%s&page=%d'

    def _real_extract(self, url):
        channel_id, programme_id = re.match(self._VALID_URL, url).groups()
        playlist_id = "%s-%s" % (channel_id, programme_id)

        entries = []
        for page in range(1, 32):
            page_data = self._download_json(self.PLAYLIST_URL_TEMPLATE % (channel_id, programme_id, page), playlist_id)
            for item in page_data['content']:
                episode_id = item['id']
                entries.append(self.parse_episode(channel_id, programme_id, episode_id))
            if page_data['nextPage'] == -1:
                break

        return self.playlist_result(entries, playlist_id)

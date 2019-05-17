# -*- coding: utf-8 -*-

# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, unicode_literals
from datetime import datetime, timedelta
import dateutil.parser
import dateutil.tz
import json

try:
    from urllib.request import build_opener, install_opener, ProxyHandler, urlopen
except ImportError:
    from urllib2 import build_opener, install_opener, ProxyHandler, urlopen

from resources.lib.helperobjects import helperobjects
from resources.lib.vrtplayer import CHANNELS, actions, metadatacreator, statichelper

DATE_STRINGS = {
    '-2': 30330,  # 2 days ago
    '-1': 30331,  # Yesterday
    '0': 30332,  # Today
    '1': 30333,  # Tomorrow
    '2': 30334,  # In 2 days
}

DATES = {
    '-1': 'yesterday',
    '0': 'today',
    '1': 'tomorrow',
}


class TVGuide:

    VRT_TVGUIDE = 'https://www.vrt.be/bin/epg/schedule.%Y-%m-%d.json'

    def __init__(self, _kodi):
        self._kodi = _kodi
        self._proxies = _kodi.get_proxies()
        install_opener(build_opener(ProxyHandler(self._proxies)))

    def show_tvguide(self, params):
        date = params.get('date')
        channel = params.get('channel')

        if not date:
            date_items = self.show_date_menu()
            self._kodi.show_listing(date_items, content='files')

        elif not channel:
            channel_items = self.show_channel_menu(date)
            self._kodi.show_listing(channel_items)

        else:
            episode_items = self.show_episodes(date, channel)
            self._kodi.show_listing(episode_items, content='episodes', cache=False)

    def show_date_menu(self):
        epg = datetime.now(dateutil.tz.tzlocal())
        # Daily EPG information shows information from 6AM until 6AM
        if epg.hour < 6:
            epg += timedelta(days=-1)
        date_items = []
        for i in range(7, -31, -1):
            day = epg + timedelta(days=i)
            title = self._kodi.localize_datelong(day)

            # Highlight today with context of 2 days
            if str(i) in DATE_STRINGS:
                if i == 0:
                    title = '[COLOR yellow][B]%s[/B], %s[/COLOR]' % (self._kodi.localize(DATE_STRINGS[str(i)]), title)
                else:
                    title = '[B]%s[/B], %s' % (self._kodi.localize(DATE_STRINGS[str(i)]), title)

            # Make permalinks for today, yesterday and tomorrow
            if str(i) in DATES:
                date = DATES[str(i)]
            else:
                date = day.strftime('%Y-%m-%d')

            date_items.append(helperobjects.TitleItem(
                title=title,
                url_dict=dict(action=actions.LISTING_TVGUIDE, date=date),
                is_playable=False,
                art_dict=dict(thumb='DefaultYear.png', icon='DefaultYear.png', fanart='DefaultYear.png'),
                video_dict=dict(plot=self._kodi.localize_datelong(day)),
            ))
        return date_items

    def show_channel_menu(self, date):
        now = datetime.now(dateutil.tz.tzlocal())
        epg = self.parse(date, now)
        # Daily EPG information shows information from 6AM until 6AM
        if epg.hour < 6:
            epg += timedelta(days=-1)
        datelong = self._kodi.localize_datelong(epg)

        fanart_path = 'resource://resource.images.studios.white/%(studio)s.png'
        icon_path = 'resource://resource.images.studios.white/%(studio)s.png'
        # NOTE: Wait for resource.images.studios.coloured v0.16 to be released
        # icon_path = 'resource://resource.images.studios.coloured/%(studio)s.png'

        channel_items = []
        for channel in CHANNELS:
            if channel.get('name') not in ('een', 'canvas', 'ketnet'):
                continue

            icon = icon_path % channel
            fanart = fanart_path % channel
            plot = '%s\n%s' % (self._kodi.localize(30301).format(**channel), datelong)
            channel_items.append(helperobjects.TitleItem(
                title=channel.get('label'),
                url_dict=dict(action=actions.LISTING_TVGUIDE, date=date, channel=channel.get('name')),
                is_playable=False,
                art_dict=dict(thumb=icon, icon=icon, fanart=fanart),
                video_dict=dict(plot=plot, studio=channel.get('studio')),
            ))
        return channel_items

    def show_episodes(self, date, channel):
        now = datetime.now(dateutil.tz.tzlocal())
        epg = self.parse(date, now)
        # Daily EPG information shows information from 6AM until 6AM
        if epg.hour < 6:
            epg += timedelta(days=-1)
        datelong = self._kodi.localize_datelong(epg)
        api_url = epg.strftime(self.VRT_TVGUIDE)
        self._kodi.log_notice('URL get: ' + api_url, 'Verbose')
        schedule = json.loads(urlopen(api_url).read())
        name = channel
        try:
            channel = next(c for c in CHANNELS if c.get('name') == name)
            episodes = schedule[channel.get('id')]
        except StopIteration:
            episodes = []
        episode_items = []
        for episode in episodes:
            metadata = metadatacreator.MetadataCreator()
            title = episode.get('title', 'Untitled')
            start = episode.get('start')
            end = episode.get('end')
            start_date = dateutil.parser.parse(episode.get('startTime'))
            end_date = dateutil.parser.parse(episode.get('endTime'))
            metadata.datetime = start_date
            url = episode.get('url')
            label = '%s - %s' % (start, title)
            metadata.tvshowtitle = title
            # NOTE: Do not use startTime and endTime as we don't want duration with seconds granularity
            start_time = dateutil.parser.parse(start)
            end_time = dateutil.parser.parse(end)
            if end_time < start_time:
                end_time = end_time + timedelta(days=1)
            metadata.duration = (end_time - start_time).total_seconds()
            metadata.plot = '[B]%s[/B]\n%s\n%s - %s\n[I]%s[/I]' % (title, datelong, start, end, channel.get('label'))
            metadata.brands = [channel.get('studio')]
            metadata.mediatype = 'episode'
            thumb = episode.get('image', 'DefaultAddonVideo.png')
            metadata.icon = thumb
            if url:
                video_url = statichelper.add_https_method(url)
                url_dict = dict(action=actions.PLAY, video_url=video_url)
                if start_date < now <= end_date:  # Now playing
                    metadata.title = '[COLOR yellow]%s[/COLOR] %s' % (label, self._kodi.localize(30302))
                else:
                    metadata.title = label
            else:
                # This is a non-actionable item
                url_dict = dict()
                if start_date < now <= end_date:  # Now playing
                    metadata.title = '[COLOR gray]%s[/COLOR] %s' % (label, self._kodi.localize(30302))
                else:
                    metadata.title = '[COLOR gray]%s[/COLOR]' % label
            episode_items.append(helperobjects.TitleItem(
                title=metadata.title,
                url_dict=url_dict,
                is_playable=True,
                art_dict=dict(thumb=thumb, icon='DefaultAddonVideo.png', fanart=thumb),
                video_dict=metadata.get_video_dict(),
            ))
        return episode_items

    def episode_description(self, episode):
        return '[B]{title}[/B]\n{start} - {end}'.format(**episode)

    def live_description(self, channel):
        now = datetime.now(dateutil.tz.tzlocal())
        epg = now
        # Daily EPG information shows information from 6AM until 6AM
        if epg.hour < 6:
            epg += timedelta(days=-1)
        api_url = epg.strftime(self.VRT_TVGUIDE)
        self._kodi.log_notice('URL get: ' + api_url, 'Verbose')
        schedule = json.loads(urlopen(api_url).read())
        name = channel
        try:
            channel = next(c for c in CHANNELS if c.get('name') == name)
            episodes = iter(schedule[channel.get('id')])
        except StopIteration:
            return ''

        description = ''
        while True:
            try:
                episode = next(episodes)
            except StopIteration:
                break
            start_date = dateutil.parser.parse(episode.get('startTime'))
            end_date = dateutil.parser.parse(episode.get('endTime'))
            if start_date < now <= end_date:  # Now playing
                description = '[COLOR yellow]%s %s[/COLOR]\n' % (self._kodi.localize(30421), self.episode_description(episode))
                try:
                    description += '%s %s' % (self._kodi.localize(30422), self.episode_description(next(episodes)))
                except StopIteration:
                    break
                break
            elif now < start_date:  # Nothing playing now, but this may be next
                description = '[COLOR yellow]%s %s[/COLOR]\n' % (self._kodi.localize(30421), self.episode_description(episode))
                try:
                    description += '%s %s' % (self._kodi.localize(30422), self.episode_description(next(episodes)))
                except StopIteration:
                    break
                break
        if not description:
            description = '[COLOR yellow]%s %s[/COLOR]\n' % (self._kodi.localize(30421), self._kodi.localize(30423))
        return description

    def parse(self, date, now):
        if date == 'today':
            return now
        if date == 'yesterday':
            return now + timedelta(days=-1)
        if date == 'tomorrow':
            return now + timedelta(days=1)
        return dateutil.parser.parse(date)

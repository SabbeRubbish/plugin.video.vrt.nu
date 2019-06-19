# -*- coding: utf-8 -*-

# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' Implements a VRTApiHelper class with common VRT NU API functionality '''

from __future__ import absolute_import, division, unicode_literals
from resources.lib import CHANNELS, CATEGORIES, metadatacreator, statichelper
from resources.lib.helperobjects import TitleItem

try:  # Python 3
    from urllib.parse import urlencode, quote, unquote
    from urllib.request import build_opener, install_opener, ProxyHandler, urlopen
except ImportError:  # Python 2
    from urllib import urlencode
    from urllib2 import build_opener, install_opener, ProxyHandler, urlopen, quote, unquote


class VRTApiHelper:
    ''' A class with common VRT NU API functionality '''

    _VRT_BASE = 'https://www.vrt.be'
    _VRTNU_SEARCH_URL = 'https://vrtnu-api.vrt.be/search'
    _VRTNU_SUGGEST_URL = 'https://vrtnu-api.vrt.be/suggest'
    _VRTNU_SCREENSHOT_URL = 'https://vrtnu-api.vrt.be/screenshots'

    def __init__(self, _kodi, _favorites):
        ''' Constructor for the VRTApiHelper class '''
        self._kodi = _kodi
        self._favorites = _favorites

        self._proxies = _kodi.get_proxies()
        install_opener(build_opener(ProxyHandler(self._proxies)))

        self._showfanart = _kodi.get_setting('showfanart', 'true') == 'true'
        self._showpermalink = _kodi.get_setting('showpermalink', 'false') == 'true'
        self._channel_filter = [channel.get('name') for channel in CHANNELS if _kodi.get_setting(channel.get('name'), 'true') == 'true']

    def get_tvshow_items(self, category=None, channel=None, feature=None, use_favorites=False):
        ''' Get all TV shows for a given category, channel or feature, optionally filtered by favorites '''
        params = dict()

        if category:
            params['facets[categories]'] = category
            cache_file = 'category.%s.json' % category

        if channel:
            params['facets[programBrands]'] = channel
            cache_file = 'channel.%s.json' % channel

        if feature:
            params['facets[programTags.title]'] = feature
            cache_file = 'featured.%s.json' % feature

        # If no facet-selection is done, we return the A-Z listing
        if not category and not channel and not feature:
            params['facets[transcodingStatus]'] = 'AVAILABLE'
            cache_file = 'programs.json'

        # Try the cache if it is fresh
        api_json = self._kodi.get_cache(cache_file, ttl=60 * 60)
        if not api_json:
            import json
            api_url = self._VRTNU_SUGGEST_URL + '?' + urlencode(params)
            self._kodi.log_notice('URL get: ' + unquote(api_url), 'Verbose')
            api_json = json.load(urlopen(api_url))
            self._kodi.update_cache(cache_file, api_json)
        return self._map_to_tvshow_items(api_json, use_favorites=use_favorites, cache_file=cache_file)

    def _map_to_tvshow_items(self, tvshows, use_favorites=False, cache_file=None):
        ''' Construct a list of TV show TitleItems based on Suggests API query and filtered by favorites '''
        tvshow_items = []
        if use_favorites:
            programs = self._favorites.programs()
        for tvshow in tvshows:
            program = statichelper.url_to_program(tvshow.get('targetUrl'))
            if use_favorites and program not in programs:
                continue
            metadata = metadatacreator.MetadataCreator()
            metadata.tvshowtitle = tvshow.get('title', '???')
            metadata.plot = statichelper.unescape(tvshow.get('description', '???'))
            metadata.brands.extend(tvshow.get('brands', []))
            metadata.permalink = statichelper.shorten_link(tvshow.get('targetUrl'))
            # NOTE: This adds episode_count to label, would be better as metadata
            # title = '%s  [LIGHT][COLOR yellow]%s[/COLOR][/LIGHT]' % (tvshow.get('title', '???'), tvshow.get('episode_count', '?'))
            label = tvshow.get('title', '???')
            if self._showfanart:
                thumbnail = statichelper.add_https_method(tvshow.get('thumbnail', 'DefaultAddonVideo.png'))
            else:
                thumbnail = 'DefaultAddonVideo.png'
            if self._favorites.is_activated():
                program_title = tvshow.get('title').encode('utf-8')
                if self._favorites.is_favorite(program):
                    context_menu = [(self._kodi.localize(30412), 'RunPlugin(%s)' % self._kodi.url_for('unfollow', title=quote(program_title), program=program))]
                else:
                    context_menu = [(self._kodi.localize(30411), 'RunPlugin(%s)' % self._kodi.url_for('follow', title=quote(program_title), program=program))]
            else:
                context_menu = []
            context_menu.append((self._kodi.localize(30413), 'RunPlugin(%s)' % self._kodi.url_for('delete_cache', cache_file=cache_file)))
            tvshow_items.append(TitleItem(
                title=label,
                path=self._kodi.url_for('programs', program=program),
                is_playable=False,
                art_dict=dict(thumb=thumbnail, icon='DefaultAddonVideo.png', fanart=thumbnail),
                video_dict=metadata.get_video_dict(),
                context_menu=context_menu,
            ))
        return tvshow_items

    def get_latest_episode(self, program):
        ''' Get the latest episode of a program '''
        import json
        video = None
        params = {
            'facets[programUrl]': statichelper.program_to_url(program, 'long'),
            'i': 'video',
            'size': '1',
        }
        api_url = self._VRTNU_SEARCH_URL + '?' + urlencode(params)
        self._kodi.log_notice('URL get: ' + unquote(api_url), 'Verbose')
        api_json = json.load(urlopen(api_url))
        if api_json.get('meta', {}).get('total_results') != 0:
            episode = list(api_json.get('results'))[0]
            video = dict(video_id=episode.get('videoId'), publication_id=episode.get('publicationId'))
        return video

    def get_episode_items(self, program=None, season=None, category=None, feature=None, programtype=None, page=None, use_favorites=False, variety=None):
        ''' Construct a list of TV show episodes TitleItems based on API query and filtered by favorites '''
        titletype = None
        all_items = True
        episode_items = []
        sort = 'episode'
        ascending = True
        content = 'episodes'

        # Recent items
        if variety in ('offline', 'recent'):
            titletype = 'recent'
            all_items = False
            page = statichelper.realpage(page)
            params = {
                'from': ((page - 1) * 50) + 1,
                'i': 'video',
                'size': 50,
            }

            if variety == 'offline':
                from datetime import datetime
                import dateutil.tz
                params['facets[assetOffTime]'] = datetime.now(dateutil.tz.gettz('Europe/Brussels')).strftime('%Y-%m-%d')

            if use_favorites:
                program_urls = [statichelper.program_to_url(p, 'long') for p in self._favorites.programs()]
                params['facets[programUrl]'] = '[%s]' % (','.join(program_urls))
                cache_file = 'my-%s-%s.json' % (variety, page)
            else:
                params['facets[programBrands]'] = '[%s]' % (','.join(self._channel_filter))
                cache_file = '%s-%s.json' % (variety, page)

            # Try the cache if it is fresh
            api_json = self._kodi.get_cache(cache_file, ttl=60 * 60)
            if not api_json:
                import json
                api_url = self._VRTNU_SEARCH_URL + '?' + urlencode(params)
                self._kodi.log_notice('URL get: ' + unquote(api_url), 'Verbose')
                api_json = json.load(urlopen(api_url))
                self._kodi.update_cache(cache_file, api_json)
            return self._map_to_episode_items(api_json.get('results', []), titletype=variety, use_favorites=use_favorites, cache_file=cache_file)

        params = {
            'i': 'video',
            'size': '150',
        }

        if program:
            params['facets[programUrl]'] = statichelper.program_to_url(program, 'long')

        if season and season != 'allseasons':
            params['facets[seasonTitle]'] = season

        if category:
            params['facets[categories]'] = category

        if feature:
            params['facets[programTags.title]'] = feature

        if programtype:
            params['facets[programType]'] = programtype

        api_url = self._VRTNU_SEARCH_URL + '?' + urlencode(params)
        results, episodes = self._get_season_episode_data(api_url, season, all_items=all_items)

        if results.get('episodes'):
            return self._map_to_episode_items(results.get('episodes', []), titletype=titletype, season=season, use_favorites=use_favorites)

        if results.get('seasons'):
            return self._map_to_season_items(program, results.get('seasons'), episodes)

        return episode_items, sort, ascending, content

    def _get_season_data(self, api_json):
        ''' Return a list of seasons '''
        facets = api_json.get('facets', dict()).get('facets')
        seasons = next((f.get('buckets', []) for f in facets if f.get('name') == 'seasons' and len(f.get('buckets', [])) > 1), None)
        return seasons

    def _get_season_episode_data(self, api_url, season, all_items=True):
        ''' Return a list of episodes for a given season '''
        import json
        self._kodi.log_notice('URL get: ' + unquote(api_url), 'Verbose')
        show_seasons = bool(not season == 'allseasons')
        api_json = json.load(urlopen(api_url))
        seasons = self._get_season_data(api_json) if 'facets[seasonTitle]' not in unquote(api_url) else None
        episodes = api_json.get('results', [{}])
        if show_seasons and seasons:
            return dict(seasons=seasons), episodes
        pages = api_json.get('meta').get('pages').get('total')
        page_size = api_json.get('meta').get('pages').get('size')
        total_results = api_json.get('meta').get('total_results')
        if all_items and total_results > page_size:
            for page in range(1, pages):
                page_url = api_url + '&from=' + str(page * page_size + 1)
                self._kodi.log_notice('URL get: ' + unquote(page_url), 'Verbose')
                page_json = json.load(urlopen(page_url))
                episodes += page_json.get('results', [{}])
        return dict(episodes=episodes), None

    def _map_to_episode_items(self, episodes, titletype=None, season=None, use_favorites=False, cache_file=None):
        ''' Construct a list of TV show episodes TitleItems based on Search API query and filtered by favorites '''
        from datetime import datetime
        import dateutil.parser
        import dateutil.tz
        now = datetime.now(dateutil.tz.tzlocal())
        sort = 'episode'
        ascending = True
        if use_favorites:
            programs = self._favorites.programs()
        episode_items = []
        for episode in episodes:
            # VRT API workaround: seasonTitle facet behaves as a partial match regex,
            # so we have to filter out the episodes from seasons that don't exactly match.
            if season and season != 'allseasons' and episode.get('seasonTitle') != season:
                continue

            program = statichelper.url_to_program(episode.get('programUrl'))
            if use_favorites and program not in programs:
                continue

            # Support search highlights
            highlight = episode.get('highlight')
            if highlight:
                for key in highlight:
                    episode[key] = statichelper.convert_html_to_kodilabel(highlight.get(key)[0])

            display_options = episode.get('displayOptions', dict())

            # NOTE: Hard-code showing seasons because it is unreliable (i.e; Thuis or Down the Road have it disabled)
            display_options['showSeason'] = True

            if titletype is None:
                titletype = episode.get('programType')

            metadata = metadatacreator.MetadataCreator()
            metadata.tvshowtitle = episode.get('program')
            if episode.get('broadcastDate') != -1:
                metadata.datetime = datetime.fromtimestamp(episode.get('broadcastDate', 0) / 1000, dateutil.tz.UTC)

            metadata.duration = (episode.get('duration', 0) * 60)  # Minutes to seconds
            metadata.plot = statichelper.convert_html_to_kodilabel(episode.get('description'))
            metadata.brands.extend(episode.get('programBrands', []) or episode.get('brands', []))
            metadata.geolocked = episode.get('allowedRegion') == 'BE'
            if display_options.get('showShortDescription'):
                short_description = statichelper.convert_html_to_kodilabel(episode.get('shortDescription'))
                metadata.plotoutline = short_description
                metadata.subtitle = short_description
            else:
                metadata.plotoutline = episode.get('subtitle')
                metadata.subtitle = episode.get('subtitle')
            metadata.season = episode.get('seasonTitle')
            metadata.episode = episode.get('episodeNumber')
            metadata.mediatype = episode.get('type', 'episode')
            metadata.permalink = statichelper.shorten_link(episode.get('permalink')) or episode.get('externalPermalink')
            if episode.get('assetOnTime'):
                metadata.ontime = dateutil.parser.parse(episode.get('assetOnTime'))
            if episode.get('assetOffTime'):
                metadata.offtime = dateutil.parser.parse(episode.get('assetOffTime'))

            # Add additional metadata to plot
            plot_meta = ''
            if metadata.geolocked:
                # Show Geo-locked
                plot_meta += self._kodi.localize(30201)
            # Only display when a video disappears if it is within the next 3 months
            if metadata.offtime is not None and (metadata.offtime - now).days < 93:
                # Show date when episode is removed
                plot_meta += self._kodi.localize(30202).format(date=self._kodi.localize_dateshort(metadata.offtime))
                # Show the remaining days/hours the episode is still available
                if (metadata.offtime - now).days > 0:
                    plot_meta += self._kodi.localize(30203).format(days=(metadata.offtime - now).days)
                else:
                    plot_meta += self._kodi.localize(30204).format(hours=int((metadata.offtime - now).seconds / 3600))

            if plot_meta:
                metadata.plot = '%s\n%s' % (plot_meta, metadata.plot)

            if self._showpermalink and metadata.permalink:
                metadata.plot = '%s\n\n[COLOR yellow]%s[/COLOR]' % (metadata.plot, metadata.permalink)

            if self._favorites.is_activated():
                program_title = episode.get('program').encode('utf-8')
                if self._favorites.is_favorite(program):
                    context_menu = [(self._kodi.localize(30412), 'RunPlugin(%s)' % self._kodi.url_for('unfollow', title=quote(program_title), program=program))]
                else:
                    context_menu = [(self._kodi.localize(30411), 'RunPlugin(%s)' % self._kodi.url_for('follow', title=quote(program_title), program=program))]
            else:
                context_menu = []
            context_menu.append((self._kodi.localize(30413), 'RunPlugin(%s)' % self._kodi.url_for('delete_cache', cache_file=cache_file)))

            if self._showfanart:
                thumb = statichelper.add_https_method(episode.get('videoThumbnailUrl', 'DefaultAddonVideo.png'))
                fanart = statichelper.add_https_method(episode.get('programImageUrl', thumb))
            else:
                thumb = 'DefaultAddonVideo.png'
                fanart = 'DefaultAddonVideo.png'
            label, sort, ascending = self._make_label(episode, titletype, options=display_options)
            metadata.title = label
            episode_items.append(TitleItem(
                title=label,
                path=self._kodi.url_for('play_id', publication_id=episode.get('publicationId'), video_id=episode.get('videoId')),
                is_playable=True,
                art_dict=dict(thumb=thumb, icon='DefaultAddonVideo.png', fanart=fanart),
                video_dict=metadata.get_video_dict(),
                context_menu=context_menu,
            ))

        return episode_items, sort, ascending, 'episodes'

    def _map_to_season_items(self, program, seasons, episodes):
        ''' Construct a list of TV show season TitleItems based on Search API query and filtered by favorites '''
        import random

        season_items = []
        sort = 'label'
        ascending = True

        episode = random.choice(episodes)
        program_type = episode.get('programType')
        if self._showfanart:
            fanart = statichelper.add_https_method(episode.get('programImageUrl', 'DefaultSets.png'))
        else:
            fanart = 'DefaultSets.png'

        metadata = metadatacreator.MetadataCreator()
        metadata.tvshowtitle = episode.get('program')
        metadata.plot = statichelper.convert_html_to_kodilabel(episode.get('programDescription'))
        metadata.plotoutline = statichelper.convert_html_to_kodilabel(episode.get('programDescription'))
        metadata.brands.extend(episode.get('programBrands', []) or episode.get('brands', []))
        metadata.geolocked = episode.get('allowedRegion') == 'BE'
        metadata.season = episode.get('seasonTitle')

        # Add additional metadata to plot
        plot_meta = ''
        if metadata.geolocked:
            # Show Geo-locked
            plot_meta += self._kodi.localize(30201) + '\n'
        metadata.plot = '%s[B]%s[/B]\n%s' % (plot_meta, episode.get('program'), metadata.plot)

        # Reverse sort seasons if program_type is 'reeksaflopend' or 'daily'
        if program_type in ('daily', 'reeksaflopend'):
            ascending = False

        # Add an "* All seasons" list item
        if self._kodi.get_global_setting('videolibrary.showallitems') is True:
            season_items.append(TitleItem(
                title=self._kodi.localize(30096),
                path=self._kodi.url_for('programs', program=program, season='allseasons'),
                is_playable=False,
                art_dict=dict(thumb=fanart, icon='DefaultSets.png', fanart=fanart),
                video_dict=metadata.get_video_dict(),
            ))

        # NOTE: Sort the episodes ourselves, because Kodi does not allow to set to 'ascending'
        seasons = sorted(seasons, key=lambda k: k['key'], reverse=not ascending)

        for season in seasons:
            season_key = season.get('key', '')
            try:
                # If more than 150 episodes exist, we may end up with an empty season (Winteruur)
                episode = random.choice([e for e in episodes if e.get('seasonName') == season_key])
            except IndexError:
                episode = episodes[0]
            if self._showfanart:
                fanart = statichelper.add_https_method(episode.get('programImageUrl', 'DefaultSets.png'))
                thumbnail = statichelper.add_https_method(episode.get('videoThumbnailUrl', fanart))
            else:
                fanart = 'DefaultSets.png'
                thumbnail = 'DefaultSets.png'
            label = '%s %s' % (self._kodi.localize(30094), season_key)
            season_items.append(TitleItem(
                title=label,
                path=self._kodi.url_for('programs', program=program, season=season_key),
                is_playable=False,
                art_dict=dict(thumb=thumbnail, icon='DefaultSets.png', fanart=fanart),
                video_dict=metadata.get_video_dict(),
            ))
        return season_items, sort, ascending, 'seasons'

    def search(self, search_string, page=0):
        ''' Search VRT NU content for a given string '''
        import json

        page = statichelper.realpage(page)
        params = {
            'from': ((page - 1) * 50) + 1,
            'i': 'video',
            'size': 50,
            'q': search_string,
            'highlight': 'true',
        }
        api_url = self._VRTNU_SEARCH_URL + '?' + urlencode(params)
        self._kodi.log_notice('URL get: ' + unquote(api_url), 'Verbose')
        api_json = json.load(urlopen(api_url))

        episodes = api_json.get('results', [{}])
        return self._map_to_episode_items(episodes, titletype='recent')

    def get_live_screenshot(self, channel):
        ''' Get a live screenshot for a given channel, only supports Eén, Canvas and Ketnet '''
        url = '%s/%s.jpg' % (self._VRTNU_SCREENSHOT_URL, channel)
        self.__delete_cached_thumbnail(url)
        return url

    def __delete_cached_thumbnail(self, url):
        ''' Remove a cached thumbnail from Kodi in an attempt to get a realtime live screenshot '''
        crc = self.__get_crc32(url)
        ext = url.split('.')[-1]
        path = 'special://thumbnails/%s/%s.%s' % (crc[0], crc, ext)
        self._kodi.delete_file(path)

    @staticmethod
    def __get_crc32(string):
        ''' Return the CRC32 checksum for a given string '''
        string = string.lower()
        string_bytes = bytearray(string.encode())
        crc = 0xffffffff
        for b in string_bytes:
            crc = crc ^ (b << 24)
            for _ in range(8):
                if crc & 0x80000000:
                    crc = (crc << 1) ^ 0x04C11DB7
                else:
                    crc = crc << 1
            crc = crc & 0xFFFFFFFF
        return '%08x' % crc

    def _make_label(self, result, titletype, options=None):
        ''' Return an appropriate label matching the type of listing and VRT NU provided displayOptions '''
        if options is None:
            options = dict()

        if options.get('showEpisodeTitle'):
            label = statichelper.convert_html_to_kodilabel(result.get('title') or result.get('shortDescription'))
        elif options.get('showShortDescription'):
            label = statichelper.convert_html_to_kodilabel(result.get('shortDescription') or result.get('title'))
        else:
            label = statichelper.convert_html_to_kodilabel(result.get('title') or result.get('shortDescription'))

        sort = 'unsorted'
        ascending = True

        if titletype in ('offline', 'recent'):
            ascending = False
            sort = 'dateadded'
            label = '[B]%s[/B] - %s' % (result.get('program'), label)

        elif titletype in ('reeksaflopend', 'reeksoplopend'):

            if titletype == 'reeksaflopend':
                ascending = False

            # NOTE: This is disable on purpose as 'showSeason' is not reliable
            if options.get('showSeason') is False and options.get('showEpisodeNumber') and result.get('seasonName') and result.get('episodeNumber'):
                try:
                    sort = 'dateadded'
                    label = 'S%02dE%02d: %s' % (int(result.get('seasonName')), int(result.get('episodeNumber')), label)
                except Exception:
                    # Season may not always be a perfect number
                    sort = 'episode'
            elif options.get('showEpisodeNumber') and result.get('episodeNumber') and ascending:
                # NOTE: Sort the episodes ourselves, because Kodi does not allow to set to 'descending'
                # sort = 'episode'
                sort = 'label'
                label = '%s %s: %s' % (self._kodi.localize(30095), result.get('episodeNumber'), label)
            elif options.get('showBroadcastDate') and result.get('formattedBroadcastShortDate'):
                sort = 'dateadded'
                label = '%s - %s' % (result.get('formattedBroadcastShortDate'), label)
            else:
                sort = 'dateadded'

        elif titletype == 'daily':
            ascending = False
            sort = 'dateadded'
            label = '%s - %s' % (result.get('formattedBroadcastShortDate'), label)

        elif titletype == 'oneoff':
            sort = 'label'
            label = result.get('program', label)

        return label, sort, ascending

    def get_channel_items(self, channels=None, live=True):
        ''' Construct a list of channel ListItems, either for Live TV or the TV Guide listing '''
        from resources.lib import tvguide
        _tvguide = tvguide.TVGuide(self._kodi)

        fanart_path = 'resource://resource.images.studios.white/%(studio)s.png'
        icon_path = 'resource://resource.images.studios.white/%(studio)s.png'
        # NOTE: Wait for resource.images.studios.coloured v0.16 to be released
        # icon_path = 'resource://resource.images.studios.coloured/%(studio)s.png'

        channel_items = []
        for channel in CHANNELS:
            if channels and channel.get('name') not in channels:
                continue

            icon = icon_path % channel
            fanart = fanart_path % channel

            if not live:
                path = self._kodi.url_for('channels', channel=channel.get('name'))
                label = channel.get('label')
                plot = '[B]%s[/B]' % channel.get('label')
                is_playable = False
                context_menu = []
            elif channel.get('live_stream') or channel.get('live_stream_id'):
                if channel.get('live_stream_id'):
                    path = self._kodi.url_for('play_id', video_id=channel.get('live_stream_id'))
                elif channel.get('live_stream'):
                    path = self._kodi.url_for('play_url', video_url=channel.get('live_stream'))
                label = self._kodi.localize(30101).format(**channel)
                # A single Live channel means it is the entry for channel's TV Show listing, so make it stand out
                if channels and len(channels) == 1:
                    label = '[B]%s[/B]' % label
                is_playable = True
                if channel.get('name') in ['een', 'canvas', 'ketnet']:
                    if self._showfanart:
                        fanart = self.get_live_screenshot(channel.get('name', fanart))
                    plot = '%s\n\n%s' % (self._kodi.localize(30102).format(**channel), _tvguide.live_description(channel.get('name')))
                else:
                    plot = self._kodi.localize(30102).format(**channel)
                context_menu = [(self._kodi.localize(30413), 'RunPlugin(%s)' % self._kodi.url_for('delete_cache', cache_file='channel.%s.json' % channel))]
            else:
                # Not a playable channel
                continue

            channel_items.append(TitleItem(
                title=label,
                path=path,
                is_playable=is_playable,
                art_dict=dict(thumb=icon, icon=icon, fanart=fanart),
                video_dict=dict(
                    title=label,
                    plot=plot,
                    studio=channel.get('studio'),
                    mediatype='video',
                ),
                context_menu=context_menu,
            ))

        return channel_items

    def get_featured_items(self):
        ''' Construct a list of featured Listitems '''
        from resources.lib import FEATURED

        featured_items = []
        for feature in FEATURED:
            featured_name = self._kodi.localize_from_data(feature.get('name'), FEATURED)
            featured_items.append(TitleItem(
                title=featured_name,
                path=self._kodi.url_for('featured', feature=feature.get('id')),
                is_playable=False,
                art_dict=dict(thumb='DefaultCountry.png', icon='DefaultCountry.png', fanart='DefaultCountry.png'),
                video_dict=dict(plot='[B]%s[/B]' % featured_name, studio='VRT'),
            ))
        return featured_items

    def get_category_items(self):
        ''' Construct a list of category ListItems '''
        categories = []

        # Try the cache if it is fresh
        categories = self._kodi.get_cache('categories.json', ttl=7 * 24 * 60 * 60)

        # Try to scrape from the web
        if not categories:
            try:
                categories = self.get_categories(self._proxies)
            except Exception:
                categories = []
            else:
                self._kodi.update_cache('categories.json', categories)

        # Use the cache anyway (better than hard-coded)
        if not categories:
            categories = self._kodi.get_cache('categories.json', ttl=None)

        # Fall back to internal hard-coded categories if all else fails
        if not categories:
            categories = CATEGORIES

        category_items = []
        for category in categories:
            if self._showfanart:
                thumbnail = category.get('thumbnail', 'DefaultGenre.png')
            else:
                thumbnail = 'DefaultGenre.png'
            category_name = self._kodi.localize_from_data(category.get('name'), CATEGORIES)
            category_items.append(TitleItem(
                title=category_name,
                path=self._kodi.url_for('categories', category=category.get('id')),
                is_playable=False,
                art_dict=dict(thumb=thumbnail, icon='DefaultGenre.png', fanart=thumbnail),
                video_dict=dict(plot='[B]%s[/B]' % category_name, studio='VRT'),
            ))
        return category_items

    def get_categories(self, proxies=None):
        ''' Return a list of categories by scraping the website '''
        from bs4 import BeautifulSoup, SoupStrainer
        self._kodi.log_notice('URL get: https://www.vrt.be/vrtnu/categorieen/', 'Verbose')
        response = urlopen('https://www.vrt.be/vrtnu/categorieen/')
        tiles = SoupStrainer('nui-list--content')
        soup = BeautifulSoup(response.read(), 'html.parser', parse_only=tiles)

        categories = []
        for tile in soup.find_all('nui-tile'):
            categories.append(dict(
                id=tile.get('href').split('/')[-2],
                thumbnail=self.get_category_thumbnail(tile),
                name=self.get_category_title(tile),
            ))

        return categories

    def get_category_thumbnail(self, element):
        ''' Return a category thumbnail, if available '''
        if self._showfanart:
            raw_thumbnail = element.find(class_='media').get('data-responsive-image', 'DefaultGenre.png')
            return statichelper.add_https_method(raw_thumbnail)
        return 'DefaultGenre.png'

    @staticmethod
    def get_category_title(element):
        ''' Return a category title, if available '''
        found_element = element.find('a')
        if found_element:
            return statichelper.strip_newlines(found_element.contents[0])
        # FIXME: We should probably fall back to something sensible here, or raise an exception instead
        return ''

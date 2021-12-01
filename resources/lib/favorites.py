# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Implementation of Favorites class"""

from __future__ import absolute_import, division, unicode_literals

try:  # Python 3
    from urllib.error import HTTPError
    from urllib.parse import unquote
except ImportError:  # Python 2
    from urllib2 import unquote

from kodiutils import (container_refresh, get_cache, get_setting_bool, get_url_json,
                       has_credentials, input_down, invalidate_caches, localize, log_error,
                       multiselect, notification, ok_dialog, update_cache)
from utils import program_to_id


class Favorites:
    """Track, cache and manage VRT favorites"""

    def __init__(self):
        """Initialize favorites, relies on XBMC vfs and a special VRT token"""
        self._data = {}  # Our internal representation

    @staticmethod
    def is_activated():
        """Is favorites activated in the menu and do we have credentials ?"""
        return get_setting_bool('usefavorites', default=True) and has_credentials()

    def refresh(self, ttl=None):
        """Get a cached copy or a newer favorites from VRT, or fall back to a cached file"""
        if not self.is_activated():
            return
        favorites_json = get_cache('favorites.json', ttl)
        if not favorites_json:
            from tokenresolver import TokenResolver
            vrttoken = TokenResolver().get_token('vrtlogin-at', variant='roaming')
            if vrttoken:
                headers = {
                    'authorization': 'Bearer ' + vrttoken,
                    'content-type': 'application/json',
                    'Referer': 'https://www.vrt.be/vrtnu',
                }
                favorites_url = 'https://www.vrt.be/vrtnu-api/graphql/v1'
                from json import dumps
                favorites_data = dict(operationName="FavoritesPage", variables='{"after": null, "pageSize": 25}', query="query FavoritesPage($pageSize: Int, $after: ID) {\n  page(id: \"custom:vrtnu-favoritePrograms\") {\n    ... on FavoritesPage {\n      title\n      components {\n        ... on PaginatedTileList {\n          __typename\n          listId\n          displayType\n          title\n          paginatedItems(first: $pageSize, after: $after) {\n            pageInfo {\n              hasNextPage\n              startCursor\n              endCursor\n              __typename\n            }\n            edges {\n              cursor\n              node {\n                __typename\n                ... on ProgramTile {\n                  id\n                  title\n                  image {\n                    objectId\n                    templateUrl\n                    __typename\n                  }\n                  available\n                  program {\n                    favorite\n                    favoriteAction {\n                      id\n                      title\n                      __typename\n                    }\n                    __typename\n                  }\n                  __typename\n                }\n              }\n              __typename\n            }\n            __typename\n          }\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n")
                favorites_bytes = dumps(favorites_data).encode("utf-8")
                favorites_json = get_url_json(url=favorites_url, cache=None, headers=headers,data=favorites_bytes)

                # We need to convert this format 
                # data.page.components[0].paginatedItems.edges array to 
                # object programName -> ...
                fetched_favorites = {}
                for f in favorites_json["data"]["page"]["components"][0]["paginatedItems"]["edges"]:
                    favorite_value={"adobeCloudId": '', "isFavorite": True, "programUrl": "/vrtnu/a-z/" + f["node"]["title"].lower().replace(".", "").replace(" ", "-"), "title": f["node"]["title"]}
                    new_favorite = {"created": 0, "updated": 0, "value": favorite_value}
                    fetched_favorites["vrtnuaz" + f["node"]["title"].lower().replace(" ", "").replace(".", "")] = (new_favorite)
                favorites_json = fetched_favorites
        if favorites_json is not None:
            from json import dumps
            self._data = favorites_json
            update_cache('favorites.json', dumps(self._data))

    def update(self, program, title, value=True):
        """Set a program as favorite, and update local copy"""

        # Survive any recent updates
        self.refresh(ttl=5)

        if value is self.is_favorite(program):
            # Already followed/unfollowed, nothing to do
            return True

        from tokenresolver import TokenResolver
        xvrttoken = TokenResolver().get_token('X-VRT-Token', variant='user')
        if xvrttoken is None:
            log_error('Failed to get favorites token from VRT NU')
            notification(message=localize(30975))
            return False

        headers = {
            'authorization': 'Bearer ' + xvrttoken,
            'content-type': 'application/json',
            'Referer': 'https://www.vrt.be/vrtnu',
        }

        from json import dumps
        from utils import program_to_url
        payload = dict(isFavorite=value, programUrl=program_to_url(program, 'short'), title=title)
        data = dumps(payload).encode('utf-8')
        program_id = program_to_id(program)
        try:
            get_url_json('https://video-user-data.vrt.be/favorites/{program_id}'.format(program_id=program_id), headers=headers, data=data, raise_errors='all')
        except HTTPError as exc:
            log_error("Failed to (un)follow program '{program}' at VRT NU ({error})", program=program, error=exc)
            notification(message=localize(30976, program=program))
            return False
        # NOTE: Updates to favorites take a longer time to take effect, so we keep our own cache and use it
        self._data[program_id] = dict(value=payload)
        update_cache('favorites.json', dumps(self._data))
        invalidate_caches('my-offline-*.json', 'my-recent-*.json')
        return True

    def is_favorite(self, program):
        """Is a program a favorite ?"""
        value = False
        favorite = self._data.get(program_to_id(program))
        if favorite:
            value = favorite.get('value', {}).get('isFavorite')
        return value is True

    def follow(self, program, title):
        """Follow your favorite program"""
        succeeded = self.update(program, title, True)
        if succeeded:
            notification(message=localize(30411, title=title))
            container_refresh()

    def unfollow(self, program, title, move_down=False):
        """Unfollow your favorite program"""
        succeeded = self.update(program, title, False)
        if succeeded:
            notification(message=localize(30412, title=title))
            # If the current item is selected and we need to move down before removing
            if move_down:
                input_down()
            container_refresh()

    def titles(self):
        """Return all favorite titles"""
        return [value.get('value').get('title') for value in list(self._data.values()) if value.get('value').get('isFavorite')]

    def programs(self):
        """Return all favorite programs"""
        from utils import url_to_program
        return [url_to_program(value.get('value').get('programUrl')) for value in list(self._data.values()) if value.get('value').get('isFavorite')]

    def manage(self):
        """Allow the user to unselect favorites to be removed from the listing"""
        from utils import url_to_program
        self.refresh(ttl=0)
        if not self._data:
            ok_dialog(heading=localize(30418), message=localize(30419))  # No favorites found
            return

        def by_title(item):
            """Sort by title"""
            return item.get('value').get('title')

        items = [dict(program=url_to_program(value.get('value').get('programUrl')),
                      title=unquote(value.get('value').get('title')),
                      enabled=value.get('value').get('isFavorite')) for value in list(sorted(list(self._data.values()), key=by_title))]
        titles = [item['title'] for item in items]
        preselect = [idx for idx in range(0, len(items) - 1) if items[idx]['enabled']]
        selected = multiselect(localize(30420), options=titles, preselect=preselect)  # Please select/unselect to follow/unfollow
        if selected is not None:
            for idx in set(preselect).difference(set(selected)):
                self.unfollow(program=items[idx]['program'], title=items[idx]['title'])
            for idx in set(selected).difference(set(preselect)):
                self.follow(program=items[idx]['program'], title=items[idx]['title'])

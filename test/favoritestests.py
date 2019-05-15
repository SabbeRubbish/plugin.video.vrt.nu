# -*- coding: utf-8 -*-

# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function, unicode_literals
import mock
import os
import unittest

from resources.lib.vrtplayer import favorites
from test import SETTINGS, get_setting, log_notice, open_file, stat_file

SETTINGS['usefavorites'] = 'true'


class TestFavorites(unittest.TestCase):

    _kodi = mock.MagicMock()
    _kodi.check_if_path_exists = mock.MagicMock(side_effect=os.path.exists)
    _kodi.get_proxies = mock.MagicMock(return_value=dict())
    _kodi.get_setting = mock.MagicMock(side_effect=get_setting)
    _kodi.get_userdata_path.return_value = './test/userdata/'
    _kodi.log_notice = mock.MagicMock(side_effect=log_notice)
    _kodi.make_dir.return_value = None
    _kodi.open_file = mock.MagicMock(side_effect=open_file)
    _kodi.stat_file = mock.MagicMock(side_effect=stat_file)
    _favorites = favorites.Favorites(_kodi)

    def test_follow_unfollow(self):
        program = 'Winteruur'
        program_path = '/vrtnu/a-z/winteruur/'
        self._favorites.follow(program, program_path)
        self.assertTrue(self._favorites.is_favorite(program_path))

        self._favorites.unfollow(program, program_path)
        self.assertFalse(self._favorites.is_favorite(program_path))

        self._favorites.follow(program, program_path)
        self.assertTrue(self._favorites.is_favorite(program_path))

    def test_names(self):
        names = self._favorites.names()
        self.assertTrue(names)
        print(names)

    def test_titles(self):
        titles = self._favorites.titles()
        self.assertTrue(titles)
        print(sorted(titles))


if __name__ == '__main__':
    unittest.main()